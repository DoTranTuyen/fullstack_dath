import React, { useEffect, useRef, useState, createContext } from "react";
import classNames from "classnames/bind";
import { IoIosClose, IoIosSearch, IoMdCloseCircle } from "react-icons/io";
import { FaSpinner } from "react-icons/fa";
import HeadlessTippy from "@tippyjs/react/headless";

import styles from "./Search.module.scss";
import ProductItem from "./ProductItem/ProductItem";
import useDebounce from "../../../../hooks/useDebounce";
import { readProduct } from "../../../../services/api";

const cx = classNames.bind(styles);
export const SearchValueContext = createContext(null);

const Search = ({ blockSearchFullscreen, handleClose }) => {
  const [searchValue, setSearchValue] = useState("");
  const [searchResult, setSearchResult] = useState([]);
  const [showResult, setShowResult] = useState(true);
  const [loading, setLoading] = useState(false);

  const debounceValue = useDebounce(searchValue, 500);

  const inputRef = useRef();
  const searchFullscreenRef = useRef();

  useEffect(() => {
    if (!searchValue.trim()) {
      setSearchResult([]);
      return;
    }
    setLoading(true);
    const fetchApi = async () => {
      setLoading(true);
      const result = await readProduct({ name: searchValue });
      setSearchResult(result?.data?.results);
      setLoading(false);
    };
    fetchApi();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debounceValue]);
  
  // handle hide result
  const handleHideResult = () => {
    setShowResult(false);
  };

  // handle clear
  const handleClear = () => {
    setSearchValue("");
    setSearchResult([]);
    inputRef.current.focus();
  };

  // handle on change
  const handleOnChang = (e) => {
    const inputValue = e.target.value;
    if (!inputValue.startsWith(" ")) {
      setSearchValue(inputValue);
    }
  };

  // handle submit
  const handleSubmit = (e) => {
    e.preventDefault();
  };

  // handle click outside to close on mobile
  useEffect(() => {
    const handleClickOutside = (event) => {
      // Check if click is on the background (outside the search area)
      if (
        searchFullscreenRef.current && 
        event.target === searchFullscreenRef.current
      ) {
        handleClose();
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [handleClose]);

  return (
    <SearchValueContext.Provider value={setSearchValue}>
      <div
        ref={searchFullscreenRef}
        className={cx(
          "search-fullscreen",
          `${blockSearchFullscreen ? "search-fullscreen-toggle" : ""}`
        )}
      >
        <div className={cx("header-search")}>
          <div>
            <HeadlessTippy
              interactive="true"
              visible={showResult && searchResult?.length > 0}
              render={(attrs) => {
                return (
                  <div className={cx("search-result")} tabIndex="-1" {...attrs}>
                    <h5 className={cx("result-title")}>Sản phẩm gợi ý</h5>
                    {searchResult && searchResult.map((apiItem, index) => {
                      return <ProductItem product={apiItem} key={`product-${index}`} />;
                    })}
                  </div>
                );
              }}
              onClickOutside={handleHideResult}
            >
              <div className={cx("search")}>
                <input
                  className={cx("input-search")}
                  value={searchValue}
                  placeholder="Tìm kiếm"
                  spellCheck={false}
                  onChange={handleOnChang}
                  ref={inputRef}
                  onFocus={() => setShowResult(true)}
                />
                {searchValue.length > 0 && (
                  <button className={cx("clear")}>
                    {!!searchValue && loading ? (
                      <FaSpinner className={cx("spinner-icon")} />
                    ) : (
                      <IoMdCloseCircle className={cx("clear-icon")} onClick={handleClear} />
                    )}
                  </button>
                )}
                <span className={cx("wall")}></span>
                <button className={cx("btn-search")} onClick={handleSubmit}>
                  <IoIosSearch className={cx("btn-search-icon")} />
                </button>
              </div>
            </HeadlessTippy>
          </div>
          <div className={cx("close")} onClick={handleClose}>
            <IoIosClose className={cx("icon-close")} />
          </div>
        </div>
      </div>
    </SearchValueContext.Provider>
  );
};

export default Search;
