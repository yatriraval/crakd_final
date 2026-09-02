import React from "react";

function Header({ status }) {
  return (
    <header className="topbar">
      <div className="brand">
        <div className="brand-mark">
          <span>⌁</span>
        </div>

        <div>
          <div className="brand-name">CRAKD</div>
          <div className="brand-subtitle">
            CYBERCRIME ANALYTICS
          </div>
        </div>
      </div>

      <div className="topbar-right">
        <div className="system-status">
          <span
            className={
              status === "online"
                ? "status-dot online"
                : "status-dot"
            }
          />

          <div>
            <span className="status-label">API STATUS</span>
            <strong>
              {status === "online"
                ? "OPERATIONAL"
                : status === "checking"
                ? "CONNECTING..."
                : "OFFLINE"}
            </strong>
          </div>
        </div>

        <div className="version">
          v1.0
        </div>
      </div>
    </header>
  );
}

export default Header;