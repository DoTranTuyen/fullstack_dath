import classNames from 'classnames/bind';
import styles from './PhoneIcon.module.scss';
import { FaPhone } from 'react-icons/fa';

const cx = classNames.bind(styles);

const PhoneIcon = () => {
    // const handlePhoneClick = () => {
    //     window.location.href = 'tel:+84774530086'; // Thay số điện thoại của bạn vào đây
    // };

    return (
        <a href='tel:0774530086' className={cx('phone-icon')}>
            <FaPhone className={cx('icon')} />
        </a>
    );
};

export default PhoneIcon;