import classNames from "classnames/bind";
import styles from "./Menu.module.scss";
import { FcSearch } from "react-icons/fc";
import { LuPizza } from "react-icons/lu";
import Food from "./Food";
import OrderSummary from "./OrderSumary";
import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useEffect, useState, useMemo } from "react";
import i18n from "../../../language/i18n";
import { toast } from 'react-toastify';
import { PulseLoader } from "react-spinners";
import { useCart } from "../../context/CartContext";
import { useAuth } from "../../context/AuthContext";
import { readSession } from "../../services/api";
import config from "../../config";
import { readCategories, readProduct } from "../../services/api";
import Pagination from "./Pagination";

const cx = classNames.bind(styles);

const MenuOrder = () => {
    const { user } = useAuth();
    const { lang } = useParams();
    const { t } = useTranslation();
    const [isFooterVisible, setIsFooterVisible] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");
    const [categories, setCategories] = useState([]);
    const [selectedCategoryId, setSelectedCategoryId] = useState("");
    const { cart } = useCart();
    const [foodItems, setFoodItems] = useState([]);

    useEffect(() => {
        const fetchCheckSessionUser = async () => {
            try {
                await readSession();
            } catch (error) {
                toast.error('Vui lòng nhập thông tin khách hàng.!', {
                    autoClose: 2000,
                    onClose: () => window.location.href = config.routes.loginMenu
                });
            }
        };
        fetchCheckSessionUser();
    }, []);

    useEffect(() => {
        if (lang) { i18n.changeLanguage(lang); }
    }, [lang]);

    useEffect(() => {
        const handleScroll = () => {
            const footer = document.getElementById("footer");
            if (footer) {
                setIsFooterVisible(footer.getBoundingClientRect().top < window.innerHeight);
            }
        };

        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                if (categories.length === 0) {
                    const response = await readCategories();
                    setCategories(response.data);
                }
            } catch (error) {
                console.error("Lỗi khi lấy danh mục:", error);
            }
        };

        fetchCategories();
    }, [categories.length]);

    useEffect(() => {
        const fetchFoodItems = async () => {
            try {
                if (foodItems.length === 0) {
                    const response = await readProduct();
                    setFoodItems(response.data.results);
                }
            } catch (error) {
                console.error("Lỗi khi lấy danh sách món ăn:", error);
            }
        };

        fetchFoodItems();
    }, [foodItems.length]);

    const filteredFoodItems = useMemo(() => {
        return foodItems.filter(item =>
            item.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
            (selectedCategoryId ? item.category_id === selectedCategoryId : true)
        );
    }, [foodItems, searchTerm, selectedCategoryId]);

    return (
        <div className={cx("container")}>
            <div className="row position-relative ps-0">
                <div className="col-12">
                    <div className={cx("image-wrapper")}>
                        <img src="https://bigboy-ecru.vercel.app/_next/image?url=%2Fbanner.png&w=828&q=80" className={`${cx("cs-img-banner")} img-fluid w-100`} alt="Banner" />
                    </div>
                    <h1 className={cx("banner-text")}>{t("menu.title")}</h1>
                    <p className={cx("banner-text-small")}>{t("menu.subtitle")}</p>
                </div>
            </div>
            <div className="row mt-3">
                <div className="col-12">
                    <div className={cx("custom-input-group", "input-group", "mb-3")}>
                        <button className={cx("custom-dropdown-btn", "btn", "btn-outline-secondary", "dropdown-toggle", "d-flex", "align-items-center")} type="button" data-bs-toggle="dropdown" aria-expanded="false">
                            <LuPizza className="me-2" />
                        </button>
                        <ul className={cx("custom-dropdown-menu", "dropdown-menu")}>
                            <li><a className="dropdown-item" href="#" onClick={() => setSelectedCategoryId("")}>{t("menu.Tất cả")}</a></li>
                            {categories.length > 0 ? categories.map(category => (
                                <li key={category.id}><a className="dropdown-item" href="#" onClick={() => setSelectedCategoryId(category.id)}>{t(`menu.${category.name}`) || category.name}</a></li>
                            )) : (
                                <li className="text-center"><PulseLoader size={10} /></li>
                            )}
                        </ul>
                        <input type="text" className={cx("custom-input", "form-control")} placeholder={t("search_placeholder")} aria-label="Text input with dropdown button" onChange={(e) => setSearchTerm(e.target.value)} />
                        <FcSearch className={cx("search-icon", "fs-4")} />
                    </div>
                </div>
            </div>
            <div className="row mt-3">
                <Food searchTerm={searchTerm} selectedCategoryId={selectedCategoryId} foodItems={filteredFoodItems} />
            </div>
            <div className={cx("row mt-3")}>
                <OrderSummary isFooterVisible={isFooterVisible} foodItems={filteredFoodItems} />
            </div>
        </div>
    );
};

export default MenuOrder;