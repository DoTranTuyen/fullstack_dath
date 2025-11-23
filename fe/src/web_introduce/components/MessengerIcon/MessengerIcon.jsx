import classNames from 'classnames/bind';
import styles from './MessengerIcon.module.scss';
import { FaFacebookMessenger } from 'react-icons/fa';

const cx = classNames.bind(styles);

const MessengerIcon = () => {
    const handleMessengerClick = () => {
        window.open('https://www.messenger.com/', '_blank');
    };

    return (
        <div className={cx('messenger-icon')} onClick={handleMessengerClick}>
            <FaFacebookMessenger className={cx('icon')} />
        </div>
    );
};

export default MessengerIcon; 