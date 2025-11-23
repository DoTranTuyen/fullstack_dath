import classNames from 'classnames/bind';
import styles from './LoginMenu.module.scss';
import { useState, useEffect } from 'react';
import { useNavigate } from "react-router-dom";
import { ClipLoader } from "react-spinners";
import { useAuth } from '../../context/AuthContext'
import { toast } from 'react-toastify';
import { useTranslation } from 'react-i18next';

const cx = classNames.bind(styles);

const LoginPage = () => {
    const { login, user } = useAuth()
    const navigate = useNavigate();
    const { t, i18n } = useTranslation();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [tableNumber, setTableNumber] = useState(null);
    const [formData, setFormData] = useState({
        phoneNumber: "",
        username: "",
        lastName: "",
        firstName: "",
    });

    useEffect(() => {
        if (user) { navigate('/menu-order/vn'); }
    }, [user, navigate]);

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        setTableNumber(params.get('table_number'));
    }, []);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        if (!formData.phoneNumber.trim()) {
            toast.error(t('login.errors.phone_required'));
            setLoading(false);
            return;
        }
        if (!/^\d{10}$/.test(formData.phoneNumber)) {
            toast.error(t('login.errors.phone_invalid'));
            setLoading(false);
            return;
        }
    
        if (!formData.firstName.trim()) {
            toast.error(t('login.errors.name_required'));
            setLoading(false);
            return;
        }

        setTimeout(async () => {
            try {
                let data = {
                    table_number: tableNumber,
                    phone_number: formData.phoneNumber,
                    username: formData.phoneNumber,
                    last_name: formData.firstName,
                    first_name: formData.firstName,
                };
                let res = await login(data);
                if (res && res.status === 200) {
                    navigate('/menu-order');
                } else {
                    toast.error(res?.response?.data?.error);
                }
            } catch (err) {
                toast.error(err?.response?.data?.error || 'An error occurred');
            } finally {
                setLoading(false);
            }
        }, 1000);
    };

    const handleChangeLanguage = (lang) => {
        i18n.changeLanguage(lang);
    };

    return (
        <div className={cx("login-container")}>
            <div className="row">
                <div className="col-12">
                    <div className={cx("login-box")}>
                       
                        <h2 className={cx("welcome-text")}>{t('login.welcome')}</h2>
                        <div className={cx("form-container")}>
                            <h3 className={cx("sign-in-text")}>{t('login.sign_in')}</h3>
                            <form onSubmit={handleSubmit}>
                                <input 
                                    type="text" 
                                    name="phoneNumber" 
                                    placeholder={t('login.phone_number')}
                                    value={formData.phoneNumber} 
                                    onChange={handleChange} 
                                />

                                <input 
                                    hidden 
                                    type="text" 
                                    name="username" 
                                    placeholder={t('login.phone_number')}
                                    value={formData.phoneNumber} 
                                    onChange={handleChange} 
                                />

                                <input 
                                    type="text" 
                                    name="firstName" 
                                    placeholder={t('login.name')}
                                    value={formData.firstName} 
                                    onChange={handleChange} 
                                />

                                <button type="submit" className={cx("arrow-button")} disabled={loading}>
                                    {loading ? <ClipLoader size={25} /> : "→"}
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;