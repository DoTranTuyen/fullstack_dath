import { useState, useEffect } from 'react';
import classNames from 'classnames/bind';
import styles from './Section.module.scss';

const cx = classNames.bind(styles);

const slides = [
  {
    "id": 1,
    "title": "Nhà hàng Fast Food",
    "text": "Thưởng thức các món ăn nhanh ngon miệng, tiện lợi và luôn sẵn sàng phục vụ bạn mọi lúc!",
    "image": "https://themewagon.github.io/feane/images/f1.png"
  },
  {
    "id": 2,
    "title": "Burger thơm ngon",
    "text": "Trải nghiệm burger nóng hổi, đầy đặn với nguyên liệu tươi ngon – làm từ tâm để bạn mê từ miếng đầu tiên!",
    "image": "https://themewagon.github.io/feane/images/f1.png"
  },
  {
    "id": 3,
    "title": "Khoai tây & Đồ uống hấp dẫn",
    "text": "Khoai tây chiên giòn rụm cùng đồ uống mát lạnh – combo hoàn hảo cho bữa ăn trọn vẹn!",
    "image": "https://themewagon.github.io/feane/images/f1.png"
  }
];

const Section = () => {
  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prevSlide) => (prevSlide + 1) % slides.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleBookTable = () => {
    const bookTableSection = document.getElementById('book-table');
    if (bookTableSection) {
      const offset = 80; // Offset để tránh bị che bởi header
      const elementPosition = bookTableSection.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - offset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  };

  return (
    <section className={cx("hero-section")}>
      <div className={cx('hero-wrapper')}>
        <div className={cx('hero-container')}>
          <div className={cx('hero-content')}>
            <h1 className={cx('hero-title')}>{slides[currentSlide].title}</h1>
            <p className={cx('hero-text')}>{slides[currentSlide].text}</p>
            <button className={cx('hero-btn')} onClick={handleBookTable}>Đặt bàn ngay</button>
          </div>
          <div className={cx('hero-image')}>
            <img src={slides[currentSlide].image} alt="Fast Food" className={cx('fade-in')} />
          </div>
        </div>
        {/* Pagination Dots */}
        <div className={cx('hero-dots')}>
          {slides.map((_, index) => (
            <span
              key={index}
              className={cx('dot', { active: index === currentSlide })}
              onClick={() => setCurrentSlide(index)}
            ></span>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Section;