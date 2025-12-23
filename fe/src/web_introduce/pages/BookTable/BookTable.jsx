import classNames from 'classnames/bind'
import styles from './BookTable.module.scss'
import { useState, useEffect } from 'react'
import { toast } from 'react-toastify'
import axios from 'axios'

const cx = classNames.bind(styles)

const BookTable = () => {
  const [formData, setFormData] = useState({
    name: '',
    phone_number: '',
    many_person: '',
    date: '',
    hour: '00:00'
  })
  const [isLoading, setIsLoading] = useState(false)
  const [minDate, setMinDate] = useState('')
  const [reservationDetail, setReservationDetail] = useState(null)
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    const today = new Date()
    const year = today.getFullYear()
    const month = String(today.getMonth() + 1).padStart(2, '0')
    const day = String(today.getDate()).padStart(2, '0')
    setMinDate(`${year}-${month}-${day}`)
  }, [])

  const handleChange = (e) => {
    const { id, value } = e.target
    setFormData((prev) => ({ ...prev, [id]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)

    const { name, phone_number, many_person, date, hour } = formData

    if (!name || !phone_number || !many_person || !date || !hour) {
      toast.error('Vui lòng điền đầy đủ thông tin!')
      setIsLoading(false)
      return
    }

    const phoneRegex = /^0\d{9}$/
    if (!phoneRegex.test(phone_number)) {
      toast.error('Số điện thoại không hợp lệ! (10 chữ số, bắt đầu bằng 0)')
      setIsLoading(false)
      return
    }

    const personNum = parseInt(many_person)
    if (isNaN(personNum) || personNum < 1) {
      toast.error('Số người phải là số nguyên >= 1!')
      setIsLoading(false)
      return
    }

    try {
      const response = await axios.post('http://192.168.20.57:8000/api/book/tables/reservations/', formData)
      toast.success(response.data.message)
      setFormData({
        name: '',
        phone_number: '',
        many_person: '',
        date: '',
        hour: '00:00'
      })
    } catch (error) {
      const res = error.response
      if (res?.data?.reservation) {
        setReservationDetail(res.data.reservation)
        toast.error('Bạn đã có đặt bàn và đây là chi tiết bàn của bạn!', {
          onClick: () => setShowModal(true),
        })
      } else {
        toast.error(res?.data?.message || 'Có lỗi xảy ra, vui lòng thử lại!')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section id="book-table" className={cx('book-table')}>
      <div className={cx('container')}>
        <div className={cx('cs-body')}>
          <div className='d-flex justify-content-center'>
            <div className='col-md-6'>
              <div className={cx('cs-booking-form')}>
                <h2 className={cx('cs-form-title', 'text-center mb-4')}>Liên hệ đặt bàn</h2>
                <form className='d-flex flex-column align-items-center' onSubmit={handleSubmit}>
                  <div className='mb-3 col-md-10 col-12'>
                    <label htmlFor='name' className={cx('cs-form-label')}>Tên của bạn:</label>
                    <input type='text' className={`form-control ${cx('cs-form-input')}`} id='name' value={formData.name} onChange={handleChange} />
                  </div>
                  <div className='mb-3 col-md-10 col-12'>
                    <label htmlFor='phone_number' className={cx('cs-form-label')}>Số điện thoại của bạn:</label>
                    <input type='tel' className={`form-control ${cx('cs-form-input')}`} id='phone_number' value={formData.phone_number} onChange={handleChange} />
                  </div>
                  <div className='mb-3 col-md-10 col-12'>
                    <label htmlFor='many_person' className={cx('cs-form-label')}>Bạn đi mấy người?</label>
                    <input type='number' min='1' className={`form-control ${cx('cs-form-input')}`} id='many_person' value={formData.many_person} onChange={handleChange} />
                  </div>
                  <div className='mb-3 col-md-10 col-12'>
                    <label htmlFor='date' className={cx('cs-form-label')}>Bạn có thể đến ngày nào?</label>
                    <input type='date' min={minDate} className={`form-control ${cx('cs-form-input')}`} id='date' value={formData.date} onChange={handleChange} />
                  </div>
                  <div className='col-md-10 col-12'>
                    <label htmlFor='hour' className={cx('cs-form-label')}>Thời gian bạn đến?</label>
                    <input type='time' className={`form-control ${cx('cs-form-input')}`} id='hour' value={formData.hour} onChange={handleChange} />
                  </div>
                  <button type='submit' className={`col-md-6 col-8 d-flex justify-content-center mt-3 ${cx('cs-submit-btn')}`} disabled={isLoading}>
                    {isLoading ? <div className="spinner-border text-light" role="status"><span className="visually-hidden">Loading...</span></div> : 'Đặt bàn ngay'}
                  </button>
                </form>
                <p className={cx('cs-note-text', 'text-center mt-3 mb-0')}>
                  Khách đặt tiệc hội nghị, liên hoan vui lòng gọi trực tiếp: <strong>1900 6750</strong>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modal chi tiết đặt bàn */}
      {showModal && reservationDetail && (
        <div className="modal fade show d-block" tabIndex="-1" role="dialog" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-dialog-centered" role="document">
            <div className="modal-content p-3">
              <div className="modal-header">
                <h5 className="modal-title">Chi tiết đặt bàn</h5>
                <button type="button" className="btn-close" onClick={() => setShowModal(false)}></button>
              </div>
              <div className="modal-body">
                <p><strong>Tên:</strong> {reservationDetail.name}</p>
                <p><strong>SĐT:</strong> {reservationDetail.phone_number}</p>
                <p><strong>Số người:</strong> {reservationDetail.many_person}</p>
                <p><strong>Ngày:</strong> {reservationDetail.date}</p>
                <p><strong>Giờ:</strong> {reservationDetail.hour}</p>
                <p><strong>Bàn:</strong> {reservationDetail.table || 'Chưa được gán'}</p>
                <p><strong>Trạng thái:</strong> {reservationDetail.status}</p>
              </div>
              <div className="modal-footer">
                <button className="btn btn-secondary" onClick={() => setShowModal(false)}>Đóng</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}

export default BookTable
