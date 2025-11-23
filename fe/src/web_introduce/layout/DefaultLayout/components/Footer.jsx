import classNames from 'classnames/bind'
import styles from './Footer.module.scss'

import { BiLogoFacebook, BiLogoTwitter, BiLogoLinkedin, BiLogoInstagram, BiLogoPinterest } from "react-icons/bi";


const cx = classNames.bind(styles)

const Footer = () => {
  return (
    <footer className={cx('cs-bg-footer')}>
      <div className={cx('container')}>
        <div className={cx('row')}>
          <div className={cx('col')}>
            <h3 className={cx('cs-head-text', 'text-center text-white')}>Liên hệ</h3>
            <p className={cx('cs-text-desc', 'text-center text-white')}>Địa chỉ</p>
            <p className={cx('cs-text-desc', 'text-center text-white')}>Gọi ngay +01 123456789</p>
            <p className={cx('cs-text-desc', 'text-center text-white')}>demo@gmail.com</p>
          </div>
          <div className={cx('col')}>
            <h3 className={cx('cs-head-text', 'text-center text-white')}>RMS</h3>
            <p className={cx('cs-text-desc', 'text-center text-white')}>Hương vị đỉnh cao – nơi ẩm thực kết nối cảm xúc. Chúng tôi mang đến trải nghiệm ăn uống đa dạng, từ món chính hấp dẫn đến đồ uống sáng tạo và món tráng miệng ngọt ngào.

</p>
            <div className={cx('cs-bl-icon')}>
              <div className={cx('cs-item-icon')}><BiLogoFacebook className={cx('cs-icon')} /></div>
              <div className={cx('cs-item-icon')}><BiLogoTwitter className={cx('cs-icon')} /></div>
              <div className={cx('cs-item-icon')}><BiLogoLinkedin className={cx('cs-icon')} /></div>
              <div className={cx('cs-item-icon')}><BiLogoInstagram className={cx('cs-icon')} /></div>
              <div className={cx('cs-item-icon')}><BiLogoPinterest className={cx('cs-icon')} /></div>
            </div>
            <p className={cx('cs-text-copyright-1')}>© 2025 Bảo lưu mọi quyền bởi RMS</p>
            <p className={cx('cs-text-copyright-2')}>© Phân phối bởi RMS</p>
          </div>
          <div className={cx('col')}>
            <h3 className={cx('cs-head-text', 'text-center text-white')}>Liên hệ</h3>
            <p className={cx('cs-text-desc', 'text-center text-white')}>Địa chỉ</p>
            <p className={cx('cs-text-desc', 'text-center text-white')}>Gọi ngay +01 123456789</p>
            <p className={cx('cs-text-desc', 'text-center text-white')}>info@rms.com</p>
            <div className={cx('cs-map')}>
              <iframe title="location-map" src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d18906.129712753736!2d6.722624160288201!3d60.12672284414915!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x463e997b1b6fc09d%3A0x6ee05405ec78a692!2sJ%C4%99zyk%20trola!5e0!3m2!1spl!2spl!4v1672239918130!5m2!1spl!2spl"></iframe>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}


export default Footer
