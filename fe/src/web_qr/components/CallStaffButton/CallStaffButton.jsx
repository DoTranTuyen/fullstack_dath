import { useContext, useEffect, useState } from 'react';
import { FaBell } from 'react-icons/fa';
import { IoClose } from "react-icons/io5";
import styles from './CallStaffButton.module.scss';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { SocketContext } from "../../../main/context/SocketContext";
import { useAuth } from '../../context/AuthContext';

const CallStaffButton = () => {
  const { session } = useAuth();
  const [bottomPosition, setBottomPosition] = useState('4rem');
  const [showModal, setShowModal] = useState(false);
  const { t } = useTranslation();
  const location = useLocation();
  const socket = useContext(SocketContext);

  useEffect(() => {
    const handleScroll = () => {
      // Nếu đang ở trang order hoặc status-order, giữ nút chuông ở vị trí cố định
      if (location.pathname.includes('/order') || location.pathname.includes('/status-order') || location.pathname.includes('/momo/payment/success')) {
        setBottomPosition('5rem');
        return;
      }

      const scrollPosition = window.scrollY + window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;

      if (documentHeight - scrollPosition < 100) {
        setBottomPosition('11rem');
      } else {
        setBottomPosition('4rem');
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [location.pathname]);

  const handleCallStaff = () => {
    setShowModal(true);
  };

  const handleConfirm = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: "staff_call",
        table_number: localStorage.getItem('table_id'),
        session: session
      }));
    }
    setShowModal(false);
  };

  const handleCancel = () => {
    setShowModal(false);
  };

  // Hide button only on login page
  if (location.pathname.includes('/login-menu')) {
    return null;
  }

  return (
    <>
      <button
        className={styles.bellButton}
        onClick={handleCallStaff}
        style={{ bottom: bottomPosition }}
      >
        <FaBell className={styles.bellIcon} />
      </button>

      {showModal && (
        <div className={styles.modalOverlay} onClick={handleCancel}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <button className={styles.closeButton} onClick={handleCancel}>
              <IoClose />
            </button>
            <h2 className={styles.modalTitle}>{t('call_staff.title')}</h2>
            <p className={styles.modalMessage}>{t('call_staff.message')}</p>
            <div className={styles.buttonGroup}>
              <button className={styles.cancelButton} onClick={handleCancel}>
                {t('call_staff.cancel')}
              </button>
              <button className={styles.confirmButton} onClick={handleConfirm}>
                {t('call_staff.confirm')}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default CallStaffButton; 