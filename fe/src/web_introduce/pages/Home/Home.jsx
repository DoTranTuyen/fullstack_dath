import classNames from "classnames/bind"
import styles from "./Home.module.scss"
import BookTable from "../BookTable/BookTable";
import About from "../About/About";
import Section from "../section/section";
import Menu from "../Menu/Menu";

const cx = classNames.bind(styles)

const Home = () => {
  return (
    <div className={cx("home")}>
      <Section />
      <Menu page='home' />
      <About page='home' />
      <BookTable />
    </div>
  );
};

export default Home;