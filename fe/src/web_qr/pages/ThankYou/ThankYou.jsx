"use client"

import { useState, useEffect } from "react"
import styles from "./ThankYou.module.scss"
import classNames from "classnames/bind"
import { Star, Download, Check, Send, Home } from "lucide-react"
import { useNavigate, useLocation } from "react-router-dom"
import axios from "axios"
import { PulseLoader } from "react-spinners"
import { jsPDF } from "jspdf"
import "jspdf-autotable"

const cx = classNames.bind(styles)

export default function ThankYou() {
  const [loading, setLoading] = useState(false)
  const [downloadLoading, setDownloadLoading] = useState(false)
  const [rating, setRating] = useState(0)
  const [hoverRating, setHoverRating] = useState(0)
  const [feedback, setFeedback] = useState("")
  const [order, setOrder] = useState(null)
  const [submitted, setSubmitted] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  // Lấy orderId từ query params
  useEffect(() => {
    const queryParams = new URLSearchParams(location.search)
    const orderId = queryParams.get("orderId")

    if (orderId) {
      fetchOrderDetails(orderId)
    }
  }, [location])

  const fetchOrderDetails = async (orderId) => {
    setLoading(true)
    try {
      // Thay thế bằng API endpoint thực tế của bạn
      const response = await axios.get(`/api/orders/${orderId}`)
      setOrder(response.data)
    } catch (error) {
      console.error("Lỗi khi lấy thông tin đơn hàng:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleRatingClick = (value) => {
    setRating(value)
  }

  const handleRatingHover = (value) => {
    setHoverRating(value)
  }

  const handleSubmitFeedback = async () => {
    if (rating === 0) return

    setLoading(true)
    try {
      // Thay thế bằng API endpoint thực tế của bạn
      await axios.post("/api/feedback", {
        orderId: order?.id,
        rating,
        feedback,
      })
      setSubmitted(true)
    } catch (error) {
      console.error("Lỗi khi gửi đánh giá:", error)
    } finally {
      setLoading(false)
    }
  }

  const downloadInvoice = async () => {
    if (!order) return

    setDownloadLoading(true)
    try {
      // Tạo PDF với jsPDF
      const doc = new jsPDF()

      // Thêm header
      doc.setFontSize(20)
      doc.text("HÓA ĐƠN", 105, 15, { align: "center" })

      // Thông tin nhà hàng
      doc.setFontSize(12)
      doc.text("Nhà hàng: Tên Nhà Hàng Của Bạn", 15, 30)
      doc.text(`Số hóa đơn: #${order.id}`, 15, 40)
      doc.text(`Ngày: ${new Date(order.created_at).toLocaleDateString("vi-VN")}`, 15, 50)
      doc.text(`Khách hàng: ${order.customer_name || "Khách hàng"}`, 15, 60)

      // Tạo bảng sản phẩm
      const tableColumn = ["STT", "Tên món", "Số lượng", "Đơn giá", "Thành tiền"]
      const tableRows = []

      // Thêm dữ liệu vào bảng
      order.items.forEach((item, index) => {
        const itemData = [
          index + 1,
          item.product_name,
          item.quantity,
          formatCurrency(item.price),
          formatCurrency(item.price * item.quantity),
        ]
        tableRows.push(itemData)
      })

      // Tạo bảng với autoTable
      doc.autoTable({
        head: [tableColumn],
        body: tableRows,
        startY: 70,
        theme: "grid",
        styles: { fontSize: 10, cellPadding: 3 },
        headStyles: { fillColor: [66, 66, 66] },
      })

      // Thêm tổng tiền
      const finalY = doc.lastAutoTable.finalY + 10
      doc.text(`Tổng tiền: ${formatCurrency(order.total_amount)}`, 150, finalY, { align: "right" })

      if (order.discount) {
        doc.text(`Giảm giá: ${formatCurrency(order.discount)}`, 150, finalY + 10, { align: "right" })
      }

      doc.text(`Thành tiền: ${formatCurrency(order.final_amount)}`, 150, finalY + 20, { align: "right" })

      // Thêm footer
      doc.text("Cảm ơn quý khách đã sử dụng dịch vụ!", 105, finalY + 40, { align: "center" })

      // Tải xuống PDF
      doc.save(`hoa-don-${order.id}.pdf`)
    } catch (error) {
      console.error("Lỗi khi tạo hóa đơn:", error)
    } finally {
      setDownloadLoading(false)
    }
  }

  // Format tiền
  const formatCurrency = (price) => {
    return price.toLocaleString("vi-VN", { style: "currency", currency: "VND" })
  }

  const goToHome = () => {
    navigate("/")
  }

  if (loading && !order) {
    return (
      <div className={cx("thank-you-container", "loading-container")}>
        <PulseLoader size={15} color={localStorage.getItem("theme") === "light" ? "#000" : "#fff"} />
      </div>
    )
  }

  return (
    <div className={cx("thank-you-container")}>
      <div className={cx("thank-you-card")}>
        <div className={cx("thank-you-header")}>
          <div className={cx("check-icon")}>
            <Check size={40} />
          </div>
          <h1>Cảm ơn bạn!</h1>
          <p>Chúng tôi đã kết thúc phiên sử dụng dịch vụ của bạn. Cảm ơn bạn đã tin tưởng và lựa chọn chúng tôi!</p>
<p>Chúng tôi rất trân trọng sự ủng hộ của bạn và luôn nỗ lực để mang lại trải nghiệm tốt nhất.</p>
<p>Nếu có bất kỳ thắc mắc hoặc góp ý nào, đừng ngần ngại liên hệ với chúng tôi. Chúc bạn một ngày tuyệt vời!</p>


        </div>

        {order && (
          <div className={cx("order-summary")}>
            <h3>Thông tin đơn hàng</h3>
            <div className={cx("order-info")}>
              <div className={cx("info-row")}>
                <span>Mã đơn hàng:</span>
                <span>#{order.id}</span>
              </div>
              <div className={cx("info-row")}>
                <span>Ngày đặt:</span>
                <span>{new Date(order.created_at).toLocaleDateString("vi-VN")}</span>
              </div>
              <div className={cx("info-row")}>
                <span>Tổng tiền:</span>
                <span>{formatCurrency(order.final_amount)}</span>
              </div>
              <div className={cx("info-row")}>
                <span>Phương thức thanh toán:</span>
                <span>{order.payment_method}</span>
              </div>
            </div>
          </div>
        )}

        <div className={cx("download-section")}>
          <button className={cx("download-button")} onClick={downloadInvoice} disabled={downloadLoading || !order}>
            {downloadLoading ? (
              <PulseLoader size={8} color="#fff" />
            ) : (
              <>
                <Download size={18} />
                Tải hóa đơn
              </>
            )}
          </button>
        </div>

        {!submitted ? (
          <div className={cx("rating-section")}>
            <h3>Đánh giá dịch vụ của chúng tôi</h3>
            <div className={cx("stars-container")}>
              {[1, 2, 3, 4, 5].map((star) => (
                <Star
                  key={star}
                  size={30}
                  onClick={() => handleRatingClick(star)}
                  onMouseEnter={() => handleRatingHover(star)}
                  onMouseLeave={() => handleRatingHover(0)}
                  className={cx("star", {
                    filled: star <= (hoverRating || rating),
                  })}
                />
              ))}
            </div>
            <textarea
              className={cx("feedback-input")}
              placeholder="Chia sẻ trải nghiệm của bạn (không bắt buộc)"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
            />
            <button className={cx("submit-button")} onClick={handleSubmitFeedback} disabled={rating === 0 || loading}>
              {loading ? (
                <PulseLoader size={8} color="#fff" />
              ) : (
                <>
                  <Send size={18} />
                  Gửi đánh giá
                </>
              )}
            </button>
          </div>
        ) : (
          <div className={cx("feedback-submitted")}>
            <div className={cx("check-icon", "small")}>
              <Check size={24} />
            </div>
            <h3>Cảm ơn bạn đã đánh giá!</h3>
            <p>Phản hồi của bạn giúp chúng tôi cải thiện dịch vụ tốt hơn.</p>
          </div>
        )}

        <div className={cx("home-button-container")}>
          <button className={cx("home-button")} onClick={goToHome}>
            <Home size={18} />
            Quay lại trang chủ
          </button>
        </div>
      </div>
    </div>
  )
}
