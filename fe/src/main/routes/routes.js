import { web_introduce } from '../../web_introduce/routes/routes'
import { web_qr } from '../../web_qr/routes/routes'

const arrayRoutes = web_introduce.concat(web_qr)

export { arrayRoutes }