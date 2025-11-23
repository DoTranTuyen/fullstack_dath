import config from "../config";
import MobileLayout from "../layout/MobileLayout";

import MenuOrder from "../pages/MenuOrder";
import Order from "../pages/Order/Order";
import LoginPage from "../pages/LoginToMenu/LoginMenu";
import Status from "../pages/StatusOrder";
import PaymentSuccess from "../pages/Payment/Payment";

const web_qr = [
  {
    path: config.routes.menuOrder,
    component: MenuOrder,
    layout: MobileLayout,
  },
  {
    path: config.routes.order,
    component: Order,
    layout: MobileLayout,
  },
  {
    path: config.routes.statusOrder,
    component: Status,
    layout: MobileLayout,
  },
  {
    path: config.routes.loginMenu,
    component: LoginPage,
    layout: MobileLayout,
  },
  {
    path: config.routes.momoPaymentSuccess,
    component: PaymentSuccess,
    layout: MobileLayout,
  },
];

export { web_qr };
