import React, { Component } from "react";
import logo from "./logo.svg";
import "./App.css";
import Node from "./Node.js";

const nodes = {
  Fropeus: {
    id: "Fropeus",
    message: "3182kbs +$3.20 \nTotal: $196.92 ",
    price: 1.23,
    total: 196.92
  },
  Luca: {
    id: "Luca",
    message: "3182kbs +$3.20 \nTotal: $296.92 ",
    price: 4.23,
    total: 296.92
  },
  Blerp: {
    id: "Blerp",
    message: "3182kbs +$3.20 \nTotal: $496.92 ",
    price: 4.23,
    total: 496.92
  },
  Dave: {
    id: "Dave",
    message: "3182kbs +$3.20 \nTotal: $596.92 ",
    price: 4.23,
    total: 596.92
  }
};

function sortNodes(nodes) {
  return Object.keys(nodes)
    .map(key => nodes[key])
    .sort((a, b) => b.total - a.total);
}

console.log(sortNodes(nodes));

class App extends Component {
  constructor(props) {
    super(props);
    this.state = { nodes: [] };
    setInterval(() => {
      this.updateNodes();
    }, 1000);
  }
  async updateNodes() {
    console.log("tryiing");
    const nodes = sortNodes(await fetch("http://10.28.7.7:3210"));
    console.log("got", nodes);
    this.setState = { nodes };
  }
  render() {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          flexWrap: "wrap",
          justifyContent: "center"
        }}
      >
        {this.state.nodes.map((node, i) => (
          <Node
            key={i}
            name={node.id}
            message={node.message}
            price={node.price}
            i={i}
          />
        ))}
      </div>
    );
  }
}

export default App;
