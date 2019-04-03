import React, { Component } from "react";
import axios from "axios";

class BoardList extends Component {
  componentDidMount() {
    this.getFiles();
  }
  state = {
    data: []
  };
  fileAPI = () => {
    return axios
      .get(`/api/board/files?id=${this.props.id}`)
      .then(response => response.data);
  };
  getFiles = async () => {
    const fileData = await this.fileAPI();
    this.setState({
      data: fileData
    });
  };
  renderFiles = () => {
    const files = this.state.data.map(data => {
      return (
        <div key={data.id}>
          <span>
            <img
              src="https://img.icons8.com/dusk/64/000000/sort-up.png"
              alt="download"
              className="download"
            />
          </span>
          <a href={"http://localhost:8000" + data.file}>{data.subject}</a>
        </div>
      );
    });
    return files;
  };
  render() {
    return (
      <div className="board-item">
        <div className="board-item-header">
          <p>
            <span className="school-name">{this.props.schoolName}</span>
            <span className="category"> {this.props.category}</span>
          </p>
          <h3 className="board-item-subject">{this.props.subject}</h3>
          <p>{this.props.postDate}</p>
        </div>
        <div>{this.props.content}</div>
        <div>{this.state.data ? this.renderFiles() : "loading..."}</div>
      </div>
    );
  }
}

export default BoardList;
