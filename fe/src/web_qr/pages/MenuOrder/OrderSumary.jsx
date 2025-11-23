import React, { useEffect, useMemo, useRef, useState } from "react";
import styles from "./Menu.module.scss";
import classNames from "classnames/bind";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { useCart } from "../../context/CartContext";

const cx = classNames.bind(styles);

export default function OrderSummary({ isFooterVisible }) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { cart } = useCart();
    const cartItems = cart?.items || [];
    const prevTotalRef = useRef({ items: 0, price: 0 });

    // Calculate total items and price
    const totalItems = useMemo(() =>
        cartItems.reduce((sum, item) => sum + item.quantity, 0),
        [cartItems]
    );

    const totalPrice = useMemo(() =>
        cartItems.reduce((sum, item) => sum + (item.quantity * item.product_price), 0),
        [cartItems]
    );

    // State for smooth transitions
    const [displayItems, setDisplayItems] = useState(totalItems);
    const [displayPrice, setDisplayPrice] = useState(totalPrice);

    // Update display values with smooth transitions
    // useEffect(() => {
    //     if (totalItems !== prevTotalRef.current.items) {
    //         setDisplayItems(totalItems);
    //         prevTotalRef.current.items = totalItems;
    //     }
    // }, [totalItems]);

    // useEffect(() => {
    //     if (totalPrice !== prevTotalRef.current.price) {
    //         setDisplayPrice(totalPrice);
    //         prevTotalRef.current.price = totalPrice;
    //     }
    // }, [totalPrice]);
    useEffect(() => {
        if (totalItems !== prevTotalRef.current.items) {
            setDisplayItems(totalItems);
            prevTotalRef.current.items = totalItems;
        }
    }, [totalItems]);

    useEffect(() => {
        if (totalPrice !== prevTotalRef.current.price) {
            setDisplayPrice(totalPrice);
            prevTotalRef.current.price = totalPrice;
        }
    }, [totalPrice]);


    const formatCurrency = (price) =>
        new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(price);

    const handleClick = () => {
        if (totalItems > 0) {
            navigate("/order");
        }
    };

    return (
        <div className={cx("order-summary", { "move-up": isFooterVisible, disabled: totalItems === 0 })}>
            <span className={cx("text")} onClick={handleClick}>
                {t("order_summary.title")} · {t("order_summary.items", { count: totalItems })}
            </span>
            <span className={cx("price", "price-animate")}>{formatCurrency(totalPrice)}</span>
        </div>
    );
}