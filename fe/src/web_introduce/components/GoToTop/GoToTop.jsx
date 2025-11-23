import { useState, useEffect } from 'react';
import classNames from 'classnames/bind';
import styles from './GoToTop.module.scss';
import { FaArrowUp } from 'react-icons/fa';

const cx = classNames.bind(styles);

const GoToTop = () => {
    const [isVisible, setIsVisible] = useState(false);

    // Show button when page is scrolled up to given distance
    const toggleVisibility = () => {
        if (window.pageYOffset > 300) {
            setIsVisible(true);
        } else {
            setIsVisible(false);
        }
    };

    // Set the top cordinate to 0
    // make scrolling smooth
    const scrollToTop = () => {
        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    };

    useEffect(() => {
        window.addEventListener("scroll", toggleVisibility);
        return () => {
            window.removeEventListener("scroll", toggleVisibility);
        };
    }, []);

    return (
        <div className={cx('go-to-top', { visible: isVisible })} onClick={scrollToTop}>
            <FaArrowUp className={cx('icon')} />
        </div>
    );
};

export default GoToTop; 