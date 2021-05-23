import React, { useState, useEffect } from "react";
import logo from "./logo.svg";
import "./App.css";

function App() {
  useEffect(() => {
    stop();
  }, []);

  const play = () => {
    fetch("/play", { method: "PUT" })
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
      });
  };

  const stop = () => {
    fetch("/stop", { method: "PUT" })
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
      });
  };

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <button onClick={play}>Play</button>
        <button onClick={stop}>Stop</button>
      </header>
    </div>
  );
}

export default App;
