import classNames from "classnames/bind"
import { useTranslation } from "react-i18next";
import styles from "./Header.module.scss"
import { RxMoon } from "react-icons/rx";
import { IoSunny } from "react-icons/io5";
import { BsBox2 } from "react-icons/bs";
import { useContext, useEffect, useState } from "react";
import { ThemeContext } from "../../../DarkMode/ThemeContext";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useLocation } from "react-router-dom";


const cx = classNames.bind(styles)

const Header = () => {

    const location = useLocation();

    //theme
    const { theme, toggleTheme } = useContext(ThemeContext);
    //translation
    const { t, i18n } = useTranslation();
    const { lang } = useParams();
    const navigate = useNavigate();

    const handleChangeLanguage = (newLang) => {
        if (lang === newLang) return;
        i18n.changeLanguage(newLang);

        const newPath = location.pathname.replace(`/${lang}`, `/${newLang}`);
        navigate(newPath, { replace: true });
    };


    const handleLogout = () => {
        navigate(`/login-menu`);
    };
    return (
        <div>
            <nav className={cx("cs-navbar", "navbar", "navbar-expand-lg", "fixed-top", {
                "navbar-light": theme === "light",
                "navbar-dark": theme === "dark",
            })}
                style={{
                    backgroundColor: theme === "dark" ? "var(--bg-color-default)" : "var(--bg-light)",
                    borderBottom: "1px solid #302d43",

                }}>
                <div className={`${cx("container")} d-flex w-100 align-items-center justify-content-between`}>
                    <div className="navbar-brand text-white d-none d-lg-block d-flex">
                        <BsBox2 className="fs-4 me-4" style={{ color: theme === "light" ? "black" : "white" }} />
                        {!location.pathname.includes("/login-menu") && (
                            <>
                                <Link to={`/menu-order/${lang}`} className="fs-6 fw-bold me-4" style={{ textDecoration: 'none', color: theme === "light" ? "black" : "white" }}>{t("home")}</Link>
                                <Link to={`/status-order`} className="fs-6 fw-bold me-4" style={{ textDecoration: 'none', color: theme === "light" ? "black" : "white" }}>{t("order")}</Link>
                            </>
                        )}
                        {/* {!location.pathname.includes("/login-menu") && (
                            <span onClick={handleLogout} className="fs-6 fw-bold me-4" style={{ cursor: "pointer", textDecoration: 'none', color: theme === "light" ? "black" : "white" }}>{t("logout")}</span>
                        )} */}
                    </div>
                    <button className={cx("navbar-toggler")}
                        type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasDarkNavbar" aria-controls="offcanvasDarkNavbar" aria-label="Toggle navigation">

                        <span className={cx("navbar-toggler-icon")}></span>
                    </button>

                    <div className="d-flex align-items-center ms-auto">
                        <div className="dropdown" data-bs-theme="dark">
                            <button className={`btn dropdown-toggle ${cx("custom-button")} d-flex align-items-center justify-content-between`} type="button" data-bs-toggle="dropdown" aria-expanded="false">
                                {t("language")}
                            </button>
                            <ul className={`dropdown-menu dropdown-menu-end ${cx("custom-dropdown")}`} aria-labelledby="dropdownMenuButtonDark">
                                <li><button className="dropdown-item" onClick={() => handleChangeLanguage("vi")}>Tiếng Việt</button></li>
                                <li><button className="dropdown-item" onClick={() => handleChangeLanguage("en")}>English</button></li>
                            </ul>
                        </div>

                        <div className="dropdown ms-3" data-bs-theme="dark">
                            <button className={`btn dropdown-toggle ${cx("custom-button-theme")} d-flex align-items-center justify-content-between text-white`} type="button" data-bs-toggle="dropdown" aria-expanded="false">
                                {theme === "dark" ? <RxMoon className={cx("icon")} /> : <IoSunny className={cx("icon")} />}
                            </button>
                            <ul className={`dropdown-menu dropdown-menu-end ${cx("custom-dropdown")}`} aria-labelledby="dropdownMenuButtonDark">
                                <li><button className="dropdown-item" onClick={() => toggleTheme("light")}><IoSunny className="me-2" style={{ fontSize: "20px" }} /> Light</button></li>
                                <li><button className="dropdown-item" onClick={() => toggleTheme("dark")}><RxMoon className="me-2" style={{ fontSize: "20px" }} /> Dark</button></li>
                            </ul>
                        </div>

                        <div className="offcanvas offcanvas-start text-bg-dark" tabIndex="-1" id="offcanvasDarkNavbar" aria-labelledby="offcanvasDarkNavbarLabel">
                            <div className="offcanvas-header align-items-center justify-content-between">
                                <BsBox2 className="fs-3" />
                                <button type="button" className="btn-close btn-close-white d-lg-none" data-bs-dismiss="offcanvas" aria-label="Close"></button>
                            </div>
                            <div className="offcanvas-body d-lg-none">
                                <ul className="navbar-nav justify-content-end flex-grow-1 pe-3">
                                    <li className="nav-item">
                                        <Link to={`/menu-order/${lang}`} className="nav-link active text-white fs-5 fw-bold" aria-current="page" href="#">{t("home")}</Link>
                                        <Link to={`/status-order/${lang}`} className="nav-link active text-white fs-5 fw-bold" aria-current="page" href="#">{t("order")}</Link>
                                    </li>
                                    {/* <li className="nav-item">
                                        <a className="nav-link text-white fs-5 fw-bold" href="#">Đăng nhập</a>
                                    </li>
                                    <li className="nav-item">
                                        <span onClick={handleLogout} className="nav-link text-white fs-5 fw-bold" href="#">Đăng Xuất</span>
                                    </li> */}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

            </nav>
        </div>
    )
}

export default Header