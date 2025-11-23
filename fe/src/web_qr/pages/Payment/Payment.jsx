import React, { useContext, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { SocketContext } from "../../../main/context/SocketContext";
import { fetchAwaitPaymentStatus } from "../../services/api";
import styles from "./Payment.module.scss";
import { useTranslation } from "react-i18next";
import { FaCheckCircle } from "react-icons/fa";

const PaymentSuccess = () => {
  const [searchParams] = useSearchParams();
  const { t } = useTranslation();
  const socket = useContext(SocketContext);
  const navigate = useNavigate();

  useEffect(() => {
    const sendResultToBackend = async () => {
      try {
        const params = Object.fromEntries(searchParams.entries());
        const response = await fetchAwaitPaymentStatus(params);
        const sessionData = response?.data?.session;

        // Notify via socket if payment is successful
        if (socket && socket.readyState === WebSocket.OPEN) {
          socket.send(
            JSON.stringify({
              type: "payment",
              session: sessionData,
            })
          );
        }
      } catch (error) {
        console.error("Error sending payment result to server:", error);
      }
    };

    sendResultToBackend();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams, socket]);

  const handleReturnToMenu = () => {
    navigate("/menu-order");
  };

  return (
    <div className={styles.container}>
      <div className={styles.thankYouCard}>
        <div className={styles.checkIcon}>
          <FaCheckCircle />
        </div>
        <div className={styles.thankYouHeader}>
          <h1>{t("payment.thank_you")}</h1>
          <p>{t("payment.success_message")}</p>
        </div>
        <button className={styles.returnButton} onClick={handleReturnToMenu}>
          {t("payment.return_to_menu")}
        </button>
      </div>
    </div>
  );
};

export default PaymentSuccess;
