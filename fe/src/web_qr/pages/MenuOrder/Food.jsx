import React, { useContext, useEffect, useState } from 'react';
import styles from "./Menu.module.scss";
import classNames from "classnames/bind";
import axios from 'axios';
import { readProduct, updateCart } from '../../services/api';
import { useCart } from '../../context/CartContext';
import Pagination from './Pagination';
import { PulseLoader } from 'react-spinners';

const cx = classNames.bind(styles);

export default function Food({ searchTerm, selectedCategoryId }) {
    const [foodItems, setFoodItems] = useState([]);
    const [quantities, setQuantities] = useState({});
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize] = useState(10);
    const [totalPages, setTotalPages] = useState(1);
    const [loading, setLoading] = useState(false);
    const { cart, addItem, updateItem, fetchCart } = useCart();

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const params = {
                    page: currentPage,
                    page_size: pageSize
                };
                if (searchTerm) params.name = searchTerm;
                if (selectedCategoryId) params.category_id = selectedCategoryId;

                const response = await readProduct(params);

                // Simulate loading delay
                setTimeout(() => {
                    setFoodItems(response.data.results);
                    setLoading(false);
                }, 1000);

                setTotalPages(Math.ceil(response.data.count / pageSize));
            } catch (error) {
                console.error("Lỗi khi lấy danh sách món ăn:", error);
                setLoading(false);
            }
        };

        fetchData();
    }, [searchTerm, selectedCategoryId, currentPage]);

    // Reset về trang 1 nếu chọn loại món ăn mới hoặc search
    useEffect(() => {
        setCurrentPage(1);
        setLoading(true); // để hiệu ứng loading khi filter thay đổi
    }, [searchTerm, selectedCategoryId]);


    useEffect(() => {
        if (cart?.items?.length) {
            const updatedQuantities = {};
            cart.items.forEach(item => {
                updatedQuantities[item.product] = item.quantity;
            });

            setQuantities(updatedQuantities);
        }
    }, [cart]);

    const increaseQuantity = async (productId) => {
        try {
            const newQuantity = (quantities[productId] || 0) + 1;
            // Update cart first
            await addItem(productId, 1);
            // Then update local state
            setQuantities(prev => ({ ...prev, [productId]: newQuantity }));
            // Finally refresh cart
            await fetchCart();
        } catch (error) {
            console.error("Error increasing quantity:", error);
            // Revert local state if API call fails
            setQuantities(prev => ({ ...prev, [productId]: quantities[productId] }));
        }
    };

    const decreaseQuantity = async (productId) => {
        const currentQuantity = quantities[productId] || 0;
        if (currentQuantity <= 0) return;

        try {
            const newQuantity = currentQuantity - 1;
            // Update cart first
            await updateItem(productId, newQuantity);
            // Then update local state
            setQuantities(prev => ({ ...prev, [productId]: newQuantity }));
            // Finally refresh cart
            await fetchCart();
        } catch (error) {
            console.error("Error decreasing quantity:", error);
            // Revert local state if API call fails
            setQuantities(prev => ({ ...prev, [productId]: quantities[productId] }));
        }
    };

    // Format tiền
    const formatCurrency = (price) => {
        return price.toLocaleString('vi-VN', { style: 'currency', currency: 'VND' });
    };

    return (
        <>
            {loading ? (
                <div className="d-flex justify-content-center my-4">
                    <PulseLoader size={15} color={localStorage.getItem("theme") === "light" ? "#000" : "#fff"} />
                </div>
            ) : (
                foodItems.map((item) => (
                    <div key={item?.id} className="col-md-6 mb-4">
                        <div className={cx("food-card")}>
                            <img src={item?.image_url} className={cx("food-image")} alt={item?.name} />
                            <div className={cx("food-info")}>
                                <h5 className={cx("food-name")}>{item?.name}</h5>
                                <p className={cx("food-description")}>{item?.description}</p>
                                <span className={cx("food-price")}>{formatCurrency(item?.price)}</span>
                            </div>
                            <div className={cx("food-add-cart")}>
                                <div className={cx("counter")}>
                                    <button className={cx("button")} onClick={() => decreaseQuantity(item?.id)}>−</button>
                                    <span className={cx("count")}>{quantities[item?.id] || 0}</span>
                                    <button className={cx("button")} onClick={() => increaseQuantity(item?.id)}>+</button>
                                </div>
                            </div>
                        </div>
                    </div>
                ))
            )}

            <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={setCurrentPage}
            />
        </>
    );
}