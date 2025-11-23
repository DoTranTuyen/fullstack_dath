import classNames from "classnames/bind";
import styles from "./Order.module.scss";
import { useTranslation } from "react-i18next";
import { useContext, useEffect, useState } from "react";
import { PulseLoader } from "react-spinners";
import { ImBin } from "react-icons/im";
import { readCart, updateQuantityCart, createInvoice } from "../../services/api";
import { useCart } from "../../context/CartContext";
import { toast } from 'react-toastify';
import { useNavigate } from "react-router-dom";
import config from "../../config";
import { FaArrowLeft } from "react-icons/fa";
import { SocketContext } from "../../../main/context/SocketContext";
import { useAuth } from "../../context/AuthContext";

const cx = classNames.bind(styles);

const Order = () => {
    const { t } = useTranslation();
    const { session } = useAuth();
    const [loading, setLoading] = useState(true);
    const { cart, setCart } = useCart();
    const cartItems = cart.items || [];
    const navigate = useNavigate()
    const socket = useContext(SocketContext);

    const fetchCart = async () => {
        setLoading(true);
        try {
            const response = await readCart();
            if (response.data && Array.isArray(response.data.items)) {
                setCart(response.data);
            } else {
                setCart({ items: [] });
            }
        } catch (error) {
            toast.error("Lỗi khi lấy giỏ hàng:", error);
            setCart({ items: [] });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchCart(); }, []);

    const handleIncreaseQuantity = async (product_id, currentQuantity) => {
        try {
            await updateQuantityCart({ product_id, quantity: currentQuantity + 1 });

            setCart((prevCart) => {
                const updatedItems = prevCart.items.map((item) =>
                    item.product === product_id ? { ...item, quantity: item.quantity + 1 } : item
                );
                return { ...prevCart, items: updatedItems };
            });
        } catch (error) {
            toast.error("Lỗi khi tăng số lượng:", error);
        }
    };

    const handleDecreaseQuantity = async (product_id, currentQuantity) => {
        if (currentQuantity <= 1) return;

        try {
            await updateQuantityCart({ product_id, quantity: currentQuantity - 1 });

            setCart((prevCart) => {
                const updatedItems = prevCart.items.map((item) =>
                    item.product === product_id ? { ...item, quantity: item.quantity - 1 } : item
                );
                return { ...prevCart, items: updatedItems };
            });
        } catch (error) {
            toast.error("Lỗi khi giảm số lượng:", error);
        }
    };

    const handleDeleteItem = async (product_id) => {
        try {
            const newItems = cart.items.filter((item) => item.product !== product_id);
            setCart({ ...cart, items: newItems });

            await updateQuantityCart({ product_id, quantity: 0 });

        } catch (error) {
            toast.error("Lỗi khi xóa sản phẩm:", error);
            fetchCart();
        }
    };


    const totalOrderPrice = cartItems.reduce((total, item) => total + item.product_price * item.quantity, 0);

    const totalQuantity = cartItems.reduce((total, item) => total + item.quantity, 0);

    const handleOrderSubmit = async () => {
        try {
            const response = await createInvoice();
            const statusCode = response?.status || response?.headers?.status;

            if (statusCode === 201) {
                if (socket && socket.readyState === WebSocket.OPEN) {
                    socket.send(
                        JSON.stringify({
                            type: "order_status",
                            session: session
                        })
                    );
                }

                toast.success("Đặt món thành công!!", {
                    autoClose: 1000,
                    onClose: async () => {
                        await new Promise(resolve => setTimeout(resolve, 50));
                        await fetchCart();
                        await setCart({ items: [] });
                        navigate(`${config.routes.statusOrder}`);
                    },
                });
            }
        } catch (error) {
            toast.error(error.response?.data?.error || "Có lỗi xảy ra khi đặt hàng!");
        }
    };


    return (
        <div className={cx("container")}>
            <div className="row">
                <div className="col-12 text-center mt-3 text-white">
                    <button
                        onClick={() => navigate("/menu-order")}
                        className={cx("back-button")}
                    >
                        <FaArrowLeft />
                    </button>
                    <h2 className={cx("order-title", "fw-bold")}>{t("order_page.title")}</h2>
                </div>
            </div>

            {loading ? (
                <div className="text-center mt-4">
                    <PulseLoader color="#ffffff" />
                </div>
            ) : cartItems.length === 0 ? (
                <div className={cx("empty-cart")}>
                    <div className={cx("empty-cart-content")}>
                        <div className={cx("empty-cart-icon")}>
                            <svg
                                width="120"
                                height="120"
                                viewBox="0 0 24 24"
                                fill="none"
                                xmlns="http://www.w3.org/2000/svg"
                            >
                                <path
                                    d="M9 22C9.55228 22 10 21.5523 10 21C10 20.4477 9.55228 20 9 20C8.44772 20 8 20.4477 8 21C8 21.5523 8.44772 22 9 22Z"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                />
                                <path
                                    d="M20 22C20.5523 22 21 21.5523 21 21C21 20.4477 20.5523 20 20 20C19.4477 20 19 20.4477 19 21C19 21.5523 19.4477 22 20 22Z"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                />
                                <path
                                    d="M1 1H5L7.68 14.39C7.77144 14.8504 8.02191 15.264 8.38755 15.5583C8.75318 15.8526 9.2107 16.009 9.68 16H19.4C19.8693 16.009 20.3268 15.8526 20.6925 15.5583C21.0581 15.264 21.3086 14.8504 21.4 14.39L23 6H6"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                />
                            </svg>
                        </div>
                        <h3>{t("order_page.empty_cart")}</h3>
                        <p>{t("order_page.empty_cart_message")}</p>
                        <button
                            className={cx("cs-btn-order")}
                            onClick={() => navigate("/menu-order")}
                        >
                            {t("order_page.continue_shopping")}
                        </button>
                    </div>
                </div>
            ) : (
                cartItems.map((item, index) => (
                    <div className="row mt-3 w-100" key={item.id}>
                        <div className="col-12">
                            <div className={cx("order-item")}>
                                <span className={cx("index")}>{index + 1}</span>
                                <img
                                    src={item.product_image_url}
                                    alt={item.product_name}
                                    className={cx("food-image")}
                                />
                                <div className={cx("order-details")}>
                                    <h4 className={cx("food-name")}>{item.product_name}</h4>
                                    <div className={cx("quantity", "mt-3", "text-white")}>
                                        <span className={cx("price")}>{(item.product_price || 0).toLocaleString()}đ</span>
                                        <span className={cx("quantity-multiplier")}> x {item.quantity}</span>
                                    </div>
                                    <div className={cx("food-add-cart")}>
                                        <div className={cx("counter")}>
                                            <button
                                                className={cx("button")}
                                                onClick={() => handleDecreaseQuantity(item.product, item.quantity)}
                                                disabled={item.quantity <= 1}
                                            >
                                                −
                                            </button>
                                            <span className={cx("count")}>{item?.quantity}</span>
                                            <button
                                                className={cx("button")}
                                                onClick={() => handleIncreaseQuantity(item.product, item.quantity)}
                                            >
                                                +
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                <span className={cx("total-price")}>
                                    {((item.product_price || 0) * (item.quantity || 0)).toLocaleString()} đ
                                </span>
                                <span className={cx("cs-deleted")} onClick={() => handleDeleteItem(item.product)}>
                                    <ImBin />
                                </span>
                            </div>
                        </div>
                    </div>
                ))
            )}

            {cartItems.length > 0 && (
                <>
                    <div className="row w-100">
                        <div className="col-12">
                            <div className={cx("order-summary")}>
                                <div className={cx("summary-content")}>
                                    <div className={cx("summary-row")}>
                                        <span className={cx("summary-label")}>{t("order_page.quantity")}</span>
                                        <span className={cx("summary-value")}>{totalQuantity} món</span>
                                    </div>
                                    <div className={cx("summary-row", "total-row")}>
                                        <span className={cx("summary-label", "total-label")}>{t("order_page.total")}</span>
                                        <span className={cx("summary-value", "total-value")}>{totalOrderPrice.toLocaleString()} đ</span>
                                    </div>
                                </div>
                                <div className={cx("order-action")}>
                                    <button
                                        type="button"
                                        className={cx("cs-btn-order")}
                                        onClick={handleOrderSubmit}
                                    >
                                        {t("order_page.button")}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default Order;