import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

// Import file ngôn ngữ
import vi from "./vn.json";
import en from "./en.json";

const getLanguageFromUrl = () => {
    const path = window.location.pathname.split('/')[1]; // Lấy phần /vi hoặc /en
    return ["vi", "en"].includes(path) ? path : "vi"; // Nếu không có thì mặc định là "vi"
};

i18n
    .use(LanguageDetector) // Tự động phát hiện ngôn ngữ
    .use(initReactI18next)
    .init({
        resources: {
            vi: { translation: vi },
            en: { translation: en }
        },
        lng: getLanguageFromUrl(), // Lấy ngôn ngữ từ URL
        fallbackLng: "vi", // Ngôn ngữ mặc định
        interpolation: {
            escapeValue: false
        }
    });

export default i18n;

/**
 * tạo obj trong file en và vn .json
 * ở các trang home nếu muốn sử dụng thì dán code dưới vào 
 *  const { lang } = useParams();
    const { t } = useTranslation();
    useEffect(() => {
        if (lang) {
            i18n.changeLanguage(lang);
        }
    }, [lang]);

    những giá trị cần thay đổi ngôn ngữ thì gán bằng    {t("menu.appetizers")}
 */