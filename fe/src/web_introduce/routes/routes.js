import config from '../config'
import DefaultLayout from '../layout/DefaultLayout'
import LoginLayout from '../layout/LoginLayout'

import Register from '../pages/Register'
import Home from '../pages/Home'
import Menu from '../pages/Menu/Menu'
import About from '../pages/About/About'
import BookTable from '../pages/BookTable/BookTable'
import ThankYou from '../../web_qr/pages/ThankYou/ThankYou'

const web_introduce = [
  {
    path: config.routes.register,
    component: Register,
    layout: LoginLayout
  },
  {
    path: config.routes.home,
    component: Home,
    layout: DefaultLayout,
  },
  {
    path: '/thank-you',
    component: ThankYou,
    layout: DefaultLayout,
  },
  {
    path: config.routes.menu,
    component: Menu,
    layout: DefaultLayout,
  },
  {
    path: config.routes.about,
    component: About,
    layout: DefaultLayout,
  },
  {
    path: config.routes.bookTable,
    component: BookTable,
    layout: DefaultLayout,
  },
]

export { web_introduce }
