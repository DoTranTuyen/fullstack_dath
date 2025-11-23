import classNames from 'classnames/bind'
import styles from './About.module.scss'
import { Carousel } from 'react-bootstrap'
import { useState } from 'react'
import { FaStar, FaStarHalfAlt, FaRegStar } from 'react-icons/fa'
import { Link } from 'react-router-dom'
import config from '../../config'

const cx = classNames.bind(styles)

const feedbackData = [
  {
    id: 1,
    name: 'Nguyễn Văn Minh',
    avatar: 'https://randomuser.me/api/portraits/men/32.jpg',
    review: 'Phở bò ở đây thực sự tuyệt vời! Nước dùng đậm đà và thịt bò mềm, thơm. Không gian nhà hàng thoáng đãng và nhân viên phục vụ rất chu đáo. Sẽ quay lại nhiều lần nữa!',
    rating: 5,
  },
  {
    id: 2,
    name: 'Trần Thị Hương',
    avatar: 'https://randomuser.me/api/portraits/women/44.jpg',
    review: 'Bánh xèo giòn rụm và nhân rất đầy đặn. Nước mắm pha đúng vị chua ngọt truyền thống. Mình đặc biệt thích chả giò và gỏi cuốn ở đây, rất tươi và thơm ngon!',
    rating: 4.5,
  },
  {
    id: 3,
    name: 'Lê Đình Tuấn',
    avatar: 'https://randomuser.me/api/portraits/men/45.jpg',
    review: 'Bún chả ở đây có hương vị đúng chuẩn Hà Nội. Thịt nướng thơm, không bị khô và nước chấm rất vừa miệng. Không khí ấm cúng làm mình nhớ đến những quán ăn ở phố cổ.',
    rating: 5,
  },
  {
    id: 4,
    name: 'Phạm Thanh Mai',
    avatar: 'https://randomuser.me/api/portraits/women/63.jpg',
    review: 'Mình tổ chức sinh nhật ở đây và rất hài lòng. Cơm niêu và các món kho tộ rất ngon, đúng vị Nam Bộ. Đặc biệt là món cá kho tộ, thịt cá mềm và thấm vị.',
    rating: 4,
  },
  {
    id: 5,
    name: 'Hoàng Đức Thành',
    avatar: 'https://randomuser.me/api/portraits/men/22.jpg',
    review: 'Các món ăn chuẩn vị miền Trung! Bún bò Huế cay thơm đúng điệu và bánh bèo thật sự ngon. Giá cả hợp lý cho chất lượng món ăn như vậy. Nhất định sẽ giới thiệu cho bạn bè.',
    rating: 4.5,
  }
]

const About = ({ page }) => {
  const [index, setIndex] = useState(0)

  const handleSelect = (selectedIndex) => {
    setIndex(selectedIndex)
  }

  // Rating stars component
  const RatingStars = ({ rating }) => {
    const stars = []
    const fullStars = Math.floor(rating)
    const hasHalfStar = rating % 1 !== 0

    for (let i = 1; i <= 5; i++) {
      if (i <= fullStars) {
        stars.push(<FaStar key={i} className={cx('star')} />)
      } else if (i === fullStars + 1 && hasHalfStar) {
        stars.push(<FaStarHalfAlt key={i} className={cx('star')} />)
      } else {
        stars.push(<FaRegStar key={i} className={cx('star')} />)
      }
    }

    return <div className={cx('rating')}>{stars}</div>
  }

  return (
    <div className={cx('wrapper')}>
      <div className={cx('container')}>
        <div className={cx('row d-flex align-items-center justify-content-center pt-5')}>
          <div className={cx('col-12 col-md-6 order-md-2', 'cs-content')}>
            <div className={cx('cs-header')}>
              <h2>Giới thiệu về nhà hàng</h2>
            </div>
            <p className={cx('cs-text')}>{`Nhà hàng ẩm thực hiện đại kết hợp với truyền thống, tạo nên tính mới lạ cho thực khách. Được ra đời vào năm 2025 với tiêu chí "Khách hàng là trên hết, phục vụ nhanh chóng" nên chúng tôi luôn tự hào về cách phục vụ cũng như các món ăn mà chúng tôi làm ra. Nhà hàng chúng tôi luôn luôn đặt khách hàng lên hàng đầu, tận tâm phục vụ, mang lại cho khách hàng những trải nghiệm tuyệt với nhất. Các món ăn với công thức độc quyền sẽ mang lại hương vị mới mẻ cho thực khách. Chúng tôi xin chân thành cảm ơn.`}</p>
            <Link to={config.routes.about} className={cx('cs-btn')}>Xem thêm</Link>
          </div>
          <div className={cx('d-none d-md-block col-md-6 order-md-1', 'cs-img')}>
            <div className={cx('cs-img-box')}><img src="https://themewagon.github.io/feane/images/about-img.png" alt="" /></div>
          </div>
        </div>
      </div>

      {/* Feedback Section */}
      {page !== 'home' && (
        <div className={cx('feedback-section')}>
          <div className={cx('container')}>
            <h2 className={cx('feedback-title')}>Cảm Nhận Của Thực Khách</h2>
            <div className={cx('feedback-subtitle')}>
              Trải nghiệm hương vị Việt Nam đích thực mà mọi người đang nói đến
            </div>
            <div className={cx('greeting-section')}>
              <p className={cx('greeting-text')}>
                <span className={cx('greeting-invitation')}>
                  Hãy cùng xem những chia sẻ từ thực khách đã trải nghiệm hương vị của chúng tôi.
                  (See what our customers say about their dining experience with us.)
                </span>
              </p>
            </div>
            <Carousel
              activeIndex={index}
              onSelect={handleSelect}
              className={cx('feedback-carousel')}
              indicators={true}
              interval={5000}
              touch={true}
            >
              {feedbackData.map((feedback) => (
                <Carousel.Item key={feedback.id}>
                  <div className={cx('feedback-item')}>
                    <div className={cx('feedback-avatar')}>
                      <img src={feedback.avatar} alt={feedback.name} />
                    </div>
                    <div className={cx('feedback-content')}>
                      <h3 className={cx('feedback-name')}>{feedback.name}</h3>
                      <RatingStars rating={feedback.rating} />
                      <p className={cx('feedback-review')}>{feedback.review}</p>
                    </div>
                  </div>
                </Carousel.Item>
              ))}
            </Carousel>
          </div>
        </div>
      )}
    </div>
  )
}

export default About