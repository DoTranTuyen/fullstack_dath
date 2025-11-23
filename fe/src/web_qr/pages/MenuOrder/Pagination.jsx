import React from "react";
import classNames from "classnames/bind";
import styles from "./Menu.module.scss";
import { FaChevronLeft, FaChevronRight } from "react-icons/fa"; // Icon mũi tên

const cx = classNames.bind(styles);

const Pagination = ({ currentPage, totalPages, onPageChange }) => {


    return (
        <div className={cx("pagination")}>
            <button
                className={cx("page-btn", { disabled: currentPage === 1 })}
                onClick={() => onPageChange(currentPage - 1)}
                disabled={currentPage === 1}
            >
                <FaChevronLeft />
            </button>

            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                <button
                    key={page}
                    className={cx("page-btn", { active: page === currentPage })}
                    onClick={() => onPageChange(page)}
                >
                    {page}
                </button>
            ))}

            <button
                className={cx("page-btn", { disabled: currentPage === totalPages })}
                onClick={() => onPageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
            >
                <FaChevronRight />
            </button>
        </div>
    );
};

export default Pagination;
