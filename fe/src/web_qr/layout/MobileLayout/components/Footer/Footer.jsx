import classNames from "classnames/bind"
import styles from "./Footer.module.scss"
import { FaTwitter, FaInstagram, FaFacebook } from "react-icons/fa";

const cx = classNames.bind(styles)

const Footer = () => {

    return (
        <footer className={cx("footer")} id="footer">
            <div className={cx("container")}>
                <div className={cx("left")}>
                    <a href="/">
                        <svg className="bi" width="30" height="24">
                            <use href="#bootstrap"></use>
                        </svg>
                    </a>
                    <span>© 2024 Company, Inc</span>
                </div>
                <div className={cx("right")}>
                    <a href="#"><FaTwitter /></a>
                    <a href="#"><FaInstagram /></a>
                    <a href="#"><FaFacebook /></a>
                </div>
            </div>
        </footer>
    )
}

export default Footer