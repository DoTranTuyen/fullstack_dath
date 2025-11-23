import React from 'react';
import CallStaffButton from '../CallStaffButton/CallStaffButton';

const Layout = ({ children }) => {
  return (
    <>
      {children}
      <CallStaffButton />
    </>
  );
};

export default Layout; 