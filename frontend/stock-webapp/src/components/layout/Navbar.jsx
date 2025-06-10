// src/components/layout/Navbar.jsx

import React from "react";
import { NavLink } from "react-router-dom";
import styles from "./Navbar.module.css";

const Navbar = () => {
  return (
    <nav className={styles.navbar}>
      <div className={styles.logo}>
        <NavLink to="/" className={styles.brand}>
          StockPredict
        </NavLink>
      </div>
      <ul className={styles.navLinks}>
        <li>
          <NavLink
            to="/news"
            className={({ isActive }) => isActive ? `${styles.link} ${styles.active}` : styles.link}
          >
            Tin tức
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/price"
            className={({ isActive }) => isActive ? `${styles.link} ${styles.active}` : styles.link}
          >
            Giá cổ phiếu
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/predict"
            className={({ isActive }) => isActive ? `${styles.link} ${styles.active}` : styles.link}
          >
            Dự đoán
          </NavLink>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;

