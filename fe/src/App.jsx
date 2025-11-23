import { BrowserRouter, Routes, Route, Navigate, useParams } from 'react-router-dom';
import { Fragment } from 'react';
import { arrayRoutes } from './main/routes/routes';
import DefaultLayout from './web_introduce/layout/DefaultLayout';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { ThemeProvider } from './web_qr/layout/DarkMode/ThemeContext';
import MobileLayout from './web_qr/layout/MobileLayout';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          {arrayRoutes.map((route, index) => {
            const Page = route.component;
            let Layout = DefaultLayout;

            if (route.layout) {
              Layout = route.layout;
            } else if (route.layout === null) {
              Layout = Fragment;
            }

            return (
              <Route
                key={index}
                path={route.path}
                element={
                  route.layout === MobileLayout ? (

                    <ThemeProvider>
                      <MobileLayout>
                        <Page />
                      </MobileLayout>
                    </ThemeProvider>

                  ) : (
                    <Layout>
                      <Page />
                    </Layout>
                  )
                }
              />
            );
          })}

          {/* Routes có ngôn ngữ ở cuối */}
          <Route path="/home/:lang" element={<DefaultLayout />} />
          <Route path="/menu/:lang" element={<DefaultLayout />} />
          <Route path="/about/:lang" element={<DefaultLayout />} />
          <Route path="/book-table/:lang" element={<DefaultLayout />} />
          <Route path="/menu-order/:lang" element={<ThemeProvider><MobileLayout /></ThemeProvider>} />
          <Route path="/order/:lang" element={<ThemeProvider><MobileLayout /></ThemeProvider>} />
          <Route path="/status-order/:lang" element={<ThemeProvider><MobileLayout /></ThemeProvider>} />

          {/* Chuyển hướng nếu không có `:lang` */}
          <Route path="/thank-you" element={<Navigate to="/thank-you" replace />} />
          <Route path="/home" element={<Navigate to="/home/vn" replace />} />
          <Route path="/menu" element={<Navigate to="/menu/vn" replace />} />
          <Route path="/about" element={<Navigate to="/about/vn" replace />} />
          <Route path="/book-table" element={<Navigate to="/book-table/vn" replace />} />

          <Route path="/menu-order" element={<Navigate to="/menu-order/vn" replace />} />
          <Route path="/order" element={<Navigate to="/order/vn" replace />} />
          <Route path="/status-order" element={<Navigate to="/status-order/vn" replace />} />

          {/* Chuyển hướng tất cả về `/home/vn` nếu không khớp */}
          <Route path="*" element={<Navigate to="/home/vn" replace />} />
        </Routes>

        <ToastContainer autoClose={1400} position="top-center" />
      </div>
    </BrowserRouter>
  );
}

export default App;
