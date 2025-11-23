import axios from "axios"

const baseUrl = import.meta.env.VITE_API_API_URL

axios.defaults.baseURL = baseUrl
axios.defaults.headers.common["Content-Type"] = "application/json"
axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = "csrftoken"
axios.defaults.xsrfHeaderName = "X-CSRFToken"

// ---------- crud function ----------
const readFunc = (data) => {
  return axios.get("/api/order", { params: data })
}
const createFunc = (data) => {
  return axios.post("/api/order", data)
}
const updateFunc = (data) => {
  return axios.put("/api/order", data)
}
const deleteFunc = (id) => {
  return axios.delete("/api/order", { params: { id } })
}

// ---------- crud table ----------
const readTable = (data) => {
  return axios.get("/api/table/list", { params: data })
}

// ---------- crud table ----------
const readProduct = (data) => {
  return axios.get("/api/products/list", { params: data })
}

// ---------- crud table ----------
const readCategory = (data) => {
  return axios.get("/api/categories", { params: data })
}

export {
  readTable, readProduct, readCategory,
}
