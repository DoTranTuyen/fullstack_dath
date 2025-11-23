import classNames from "classnames/bind";
import styles from "./Status.module.scss";
import { useTranslation } from "react-i18next";
import { useContext, useEffect, useState } from "react";
import { PulseLoader } from "react-spinners";
import { ImBin } from "react-icons/im";
import { IoClose } from "react-icons/io5";
import { FaStar } from "react-icons/fa";
import {

  readInvoice,
  deleteCartItem,
  getAwaitMomoPayment,

} from "../../services/api";
import { useCart } from "../../context/CartContext";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { SocketContext } from "../../../main/context/SocketContext";
import { useAuth } from "../../context/AuthContext";
const cx = classNames.bind(styles);

const Status = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const { cart, setCart } = useCart();
  const cartItems = cart.items || [];
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState(null);
  const [showCashConfirmation, setShowCashConfirmation] = useState(false);
  const [orderDetails, setOrderDetails] = useState([]);
  const navigate = useNavigate();
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [rating, setRating] = useState(0);
  const [hover, setHover] = useState(0);
  const [feedback, setFeedback] = useState("");
  const socket = useContext(SocketContext);
  const { session } = useAuth();
  // Tính tổng tiền
  const totalAmount = orderDetails.reduce((total, item) => {
    return total + item.product_price * item.quantity;
  }, 0);

  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('data', data)
        if (data?.type === "product_status" && data?.data.product_status) {
          fetchInvoice();
        }
      } catch (err) {
        console.error("Error parsing message:", err);
      }
    };
  }

  const getStatusProductOrderENToVN = (status) => {
    switch (status) {
      case "pending":
        return "chờ";
      case "in_progress":
        return "đang làm";
      case "completed":
        return "hoàn thành";
      case "cancelled":
        return "hủy";
      default:
        return "";
    }
  };

  // Format tiền tệ
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("vi-VN", {
      style: "currency",
      currency: "VND",
    }).format(amount);
  };

  const fetchInvoice = async () => {
    try {
      const invoice = await readInvoice(); // Gọi API
      const orders = invoice.data.orders || [];
      // Gộp tất cả order_details từ các đơn hàng
      const allOrderDetails = orders.flatMap(
        (order) => order.order_details || []
      );
      setOrderDetails(allOrderDetails);
    } catch (error) {
      // toast.error("Lỗi khi lấy hóa đơn:", error);
    } finally {
      setLoading(false);
    }
  };

  // Lấy giỏ hàng
  useEffect(() => {
    fetchInvoice();
  }, []);

  // Xử lý xóa item
  const handleDeleteItem = async (productId) => {
    try {
      await deleteCartItem(productId);
    } catch (error) {
      toast.error("Lỗi khi xóa sản phẩm:", error);
    }
  };

  // Xử lý đóng modal
  const handleCloseModal = () => {
    setShowPaymentModal(false);
    setSelectedPaymentMethod(null);
    setShowCashConfirmation(false);
  };

  // Xử lý xác nhận thanh toán
  const handleConfirmPayment = () => {
    // Xử lý logic thanh toán ở đây
    toast.success("Yêu cầu thanh toán đã được gửi đến hệ thống!");
    handleCloseModal();

    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(
        JSON.stringify({
          type: "required_payment_cash",
          session: session
        })
      );
    }

    // Chuyển hướng sang trang payment success sau 3 giây
    setTimeout(() => {
      navigate("/momo/payment/success");
    }, 5000);
  };

  // Xử lý gửi đánh giá
  const handleSubmitRating = () => {
    if (rating === 0) {
      toast.warning(t("status_order.rating_warning"));
      return;
    }
    toast.success(t("status_order.rating_success"));
    setShowRatingModal(false);
    setRating(0);
    setFeedback("");
  };

  // URL QR code (tạm thời)
  const qrCodeUrl =
    "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=example";

  const handlePayment = (method) => {
    setSelectedPaymentMethod(method);
    if (method === "cash") {
      setShowCashConfirmation(true);
    }
  };

  const handleCashConfirm = () => {
    // Xử lý thanh toán tiền mặt
    toast.success("Thanh toán thành công");
    setShowCashConfirmation(false);
    setShowPaymentModal(false);
  };

  const handleCloseQR = () => {
    setSelectedPaymentMethod(null);
  };

  // Lấy trạng thái đơn hàng
  const getStatusClass = (status) => {
    switch (status.toLowerCase()) {
      case "chờ":
        return "pending";
      case "đang làm":
        return "confirmed";
      case "hủy":
        return "canceled";
      case "hoàn thành":
        return "completed";
      default:
        return "";
    }
  };


  const getAsyncMomoPayment = async () => {

    try {
      const response = await getAwaitMomoPayment(); // gọi API Django
      const payUrl = response?.data?.payUrl;
      if (payUrl) {
        // Redirect user tới trang thanh toán Momo
        window.location.href = payUrl;
      }
    } catch (error) {
      console.error("Lỗi khi xử lý thanh toán:", error);

    }
  };

  // Xử lý đóng modal đánh giá
  const handleCloseRating = () => {
    setShowRatingModal(false);
    setRating(0);
    setFeedback("");
  };

  return (
    <div className={cx("container")}>
      <div className="row">
        <div className="col-12 text-center mt-3 text-white">
          <h2 className={cx("cs-title", "fw-bold")}>
            {t("status_order.title")}
          </h2>
        </div>
      </div>

      {loading ? (
        <div className="text-center mt-4">
          <PulseLoader color="#ffffff" />
        </div>
      ) : orderDetails.length === 0 ? (
        <div className={cx("empty-status")}>
          <div className={cx("empty-status-content")}>
            <h3>{t("status_order.empty_title")}</h3>
            <p className="text-center">{t("status_order.empty_message")}</p>
            <Link to="/menu-order" className={cx("cs-btn-order")}>
              {t("order_page.button")}
            </Link>
          </div>
        </div>
      ) : (
        <>
          {orderDetails.map((item, index) => (
            <div
              className="row mt-3 w-100"
              key={`${item.product_id}-${item.order_id}-${index}`}
            >
              <div className="col-12"></div>
              <div className={cx("order-item")}>
                <img
                  src={item.product_image_url}
                  alt={item.product_name}
                  className={cx("food-image")}
                />
                <div className={cx("order-details")}>
                  <h4 className={cx("food-name")}>{item.product_name}</h4>
                  <div className={cx("quantity", "mt-3", "text-white")}>
                    <span className={cx("quantity-multiplier")}>
                      {" "}
                      x {item.quantity}
                    </span>
                  </div>
                  <div className={cx("cs-status", getStatusClass(item.status))}>
                    <span className={cx("cs-sub-status")}>
                      {t(`status_order.status.${getStatusClass(item.status)}`)}
                    </span>
                  </div>
                </div>

                {/* <span className={cx("cs-deleted")}>
                  <ImBin />
                </span> */}
              </div>
            </div>
          ))}

          <div className="row mt-3 pb-3">
            <div className="col-6">
              <button
                type="button"
                className={cx("cs-btn-order")}
                onClick={() => navigate("/menu-order")}
              >
                {t("status_order.add_more")}
              </button>
            </div>
            <div className="col-6">
              <button
                type="button"
                className={cx("cs-btn-order")}
                onClick={() => setShowPaymentModal(true)}
              >
                {t("status_order.payment")}
              </button>
            </div>
          </div>
        </>
      )}

      {/* Payment Modal */}
      {showPaymentModal && (
        <div className={styles["modal-overlay"]} onClick={handleCloseModal}>
          <div
            className={styles["modal-content"]}
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className={styles["modal-title"]}>
              {t("status_order.payment_method")}
            </h2>
            <div className={styles["payment-options"]}>
              <button
                className={styles["payment-option"]}
                onClick={getAsyncMomoPayment}
              >
                <i className="fas fa-money-bill-wave"></i>
                {t("status_order.momo_payment")}
              </button>
              <button
                className={styles["payment-option"]}
                onClick={() => setSelectedPaymentMethod("cash")}
              >
                <i className="fas fa-money-bill-wave"></i>
                {t("status_order.cash_payment")}
              </button>
              <button
                className={styles["payment-option"]}
                onClick={() => setSelectedPaymentMethod("bank")}
              >
                <i className="fas fa-university"></i>
                {t("status_order.bank_transfer")}
              </button>
            </div>

            {selectedPaymentMethod === "cash" && (
              <div className={styles["cash-confirmation"]}>
                <h3 className={styles["confirmation-title"]}>
                  {t("status_order.cash_confirm_title")}
                </h3>
                <div className={styles["confirmation-content"]}>
                  <p className={styles["confirmation-text"]}>
                    {t("status_order.cash_confirm_message", {
                      amount: formatCurrency(totalAmount),
                    })}
                  </p>
                  <div className={styles["confirmation-buttons"]}>
                    <button
                      className={styles["confirm-button"]}
                      onClick={handleConfirmPayment}
                    >
                      {t("status_order.confirm")}
                    </button>
                    <button
                      className={styles["cancel-button"]}
                      onClick={() => setSelectedPaymentMethod(null)}
                    >
                      {t("status_order.cancel")}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {selectedPaymentMethod === "bank" && (
              <div className={styles["qr-section"]}>
                <div className={styles["qr-title"]}>
                  {t("status_order.qr_title")}
                  <button
                    className={styles["qr-close"]}
                    onClick={handleCloseQR}
                  >
                    <IoClose />
                  </button>
                </div>
                <div className={styles["qr-container"]}>
                  <img
                    src={qrCodeUrl}
                    alt="QR Code"
                    className={styles["qr-code"]}
                  />
                </div>
                <p className={styles["qr-instruction"]}>
                  {t("status_order.qr_instruction")}
                </p>
              </div>
            )}

            {!selectedPaymentMethod && (
              <button
                className={styles["close-modal"]}
                onClick={handleCloseModal}
              >
                {t("status_order.close")}
              </button>
            )}
          </div>
        </div>
      )}

      {/* Rating Modal */}
      {showRatingModal && (
        <div className={styles["modal-overlay"]} onClick={handleCloseRating}>
          <div
            className={styles["modal-content"]}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              className={styles["close-rating"]}
              onClick={handleCloseRating}
            >
              <IoClose />
            </button>
            <div className={styles["modal-header"]}>
              <h2 className={styles["modal-title"]}>
                {t("status_order.rating_title")}
              </h2>
            </div>
            <div className={styles["rating-section"]}>
              <div className={styles["star-rating"]}>
                {[...Array(5)].map((star, index) => {
                  const ratingValue = index + 1;
                  return (
                    <label key={index}>
                      <input
                        type="radio"
                        name="rating"
                        value={ratingValue}
                        onClick={() => setRating(ratingValue)}
                      />
                      <FaStar
                        className={styles["star"]}
                        color={
                          ratingValue <= (hover || rating)
                            ? "#ffc107"
                            : "#e4e5e9"
                        }
                        size={40}
                        onMouseEnter={() => setHover(ratingValue)}
                        onMouseLeave={() => setHover(0)}
                      />
                    </label>
                  );
                })}
              </div>
              <textarea
                className={styles["feedback-input"]}
                placeholder={t("status_order.feedback_placeholder")}
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
              />
              <button
                className={styles["submit-rating"]}
                onClick={handleSubmitRating}
              >
                {t("status_order.submit_rating")}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Status;
