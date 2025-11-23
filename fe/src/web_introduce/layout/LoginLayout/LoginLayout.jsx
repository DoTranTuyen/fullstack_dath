import classNames from 'classnames/bind'
import styles from './LoginLayout.module.scss'
import Header from './components/Header'
import Footer from './components/Footer'

const cx = classNames.bind(styles)

const LoginLayout = ({ children }) => {
  return (
    <div>
      <Header/>
      <div className={cx('container')}>{children}</div>
      <Footer />
    </div>
  )
}


export default LoginLayout
