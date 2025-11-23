import axios from "axios"

const baseUrl = import.meta.env.VITE_API_API_URL

axios.defaults.baseURL = baseUrl
axios.defaults.headers.common["Content-Type"] = "application/json"
axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = "csrftoken"
axios.defaults.xsrfHeaderName = "X-CSRFToken"

const loginAccount = (data) => { return axios.post('/api/auth/login/', data, { headers: { 'Content-Type': 'application/json' }, withCredentials: true }) }
const readSession = () => { return axios.get("/api/auth/session/") }

const readCart = (data) => { return axios.get("/api/cart/me/", { params: data }) }
const updateCart = (data) => { return axios.post("/api/cart/add-item/", data) }
const updateQuantityCart = (data) => { return axios.put("/api/cart/update-item/", data) }
const deleteCartItem = (id) => { return axios.delete("/api/order", { params: { id } }) }

const readCategories = (data) => { return axios.get("/api/categories/", { params: data }) }
const readProduct = (data) => { return axios.get("/api/products/list/", { params: data }) }
const createInvoice = (data) => axios.post("/api/invoices/");
const readInvoice = (data) => axios.get("/api/invoices/current/", { params: data })
const getAwaitMomoPayment = () => {
  return axios.post("/api/invoices/payment/");
};
const fetchAwaitPaymentStatus = (data) => {
  return axios.post("/api/invoices/momo-ipn/",data);
};
const endSession = () => {
  return axios.get("/api/end-session/");
};


export {
  loginAccount, readSession,
  updateCart, updateQuantityCart, readCart, deleteCartItem, readCategories, readProduct, createInvoice, readInvoice,
  getAwaitMomoPayment,
  fetchAwaitPaymentStatus,
  endSession
}
