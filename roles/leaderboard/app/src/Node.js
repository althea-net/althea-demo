import React, { Component } from "react";

const styles = {
  title: {
    textAlign: "center",
    fontFamily: "Rajdhani, sans-serif",
    fontWeight: 600
  },
  screen: {
    backgroundColor: "#24118E",
    width: 400,
    color: "white",
    paddingLeft: 30,
    paddingRight: 30,
    paddingTop: 10,
    paddingBottom: 10,
    margin: 0,
    marginBottom: 5
  }
};

export default ({ name, message, price, i, lastUpdated, total }) => {
  let backgroundImage;
  let baseColor;
  let place;
  switch (i) {
    case 0:
      place = "1st";
      baseColor = "#FFC229";
      backgroundImage = "linear-gradient(-45deg, #B18C1B, #FFC229)";
      break;
    case 1:
      place = "2nd";
      baseColor = "#F2F2F2";
      backgroundImage = "linear-gradient(-45deg, #A1A1A1, #F2F2F2)";
      break;
    case 2:
      place = "3rd";
      baseColor = "#D59653";
      backgroundImage = "linear-gradient(-45deg, #85643D, #D59653)";
      break;
    default:
      place = false;
      backgroundImage = false;
  }
  return (
    <div
      style={{
        display: "flex",
        position: "relative",
        flexDirection: "column",
        alignItems: "center",
        padding: 10,
        marginLeft: 20,
        marginRight: 20,
        marginTop: 30,
        marginBottom: 10,
        borderRadius: 10,
        backgroundImage
      }}
    >
      {place && (
        <div
          style={{
            position: "absolute",
            top: -30,
            left: -50,
            height: 80,
            width: 100,
            backgroundColor: baseColor,
            borderRadius: 1000,
            fontSize: 48,
            textAlign: "center",
            paddingTop: 20,
            fontFamily: "Rajdhani, sans-serif",
            fontWeight: 600,
            transform: "rotate(-10deg)"
          }}
        >
          {place}
        </div>
      )}
      <div style={{ ...styles.title, fontSize: 64 }}>{name}</div>
      <pre style={{ ...styles.screen, fontSize: 64 }}>${total.toFixed(2)}</pre>
      <div style={{ ...styles.title, fontSize: 48 }}>
        Price per GB: <b>${(price / 100).toFixed(2)}</b>
      </div>
    </div>
  );
};
