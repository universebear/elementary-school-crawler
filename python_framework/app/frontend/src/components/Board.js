import React, { Component } from "react";
import "../style/Board.scss";
import BoardList from "./BoardList";
import Axios from "axios";

class Board extends Component {
  state = {
    results: [],
    next: null,
    count: 0
  };
  componentDidMount() {
    this.getList();
    console.log(this.state);
    window.addEventListener("scroll", this.infiniteScroll, true);
  }

  callAPI = url => {
    return Axios.get(url).then(response => response.data);
  };
  getList = async (url = "/api/board/") => {
    const board = await this.callAPI(/api.+/.exec(url));
    this.setState({
      ...board,
      results: [...this.state.results, ...board.results],
      next: board.next
    });
    console.log(this.state);
  };
  callSelectApi = url => {
    return Axios.get(url).then(response => response.data);
  };
  getSelectList = async () => {
    const selectUrl = `/api/board/select`;
    const selectBoard = await this.callSelectApi(selectUrl);
    if (selectBoard.status === false) {
      return (document.querySelector(
        "body"
      ).innerHTML += `<div class="notification notification-error">업데이트된 내용이 없습니다.</div>`);
    } else if (selectBoard.status === true) {
      this.getList();
      return (document.querySelector(
        "body"
      ).innerHTML += `<div class="notification notification-success">데이터가 업데이트 되었습니다.</div>`);
    }
    console.log(selectBoard);
  };

  infiniteScroll = () => {
    let scrollHeight = Math.max(
      document.documentElement.scrollHeight,
      document.body.scrollHeight
    );
    let scrollTop = Math.max(
      document.documentElement.scrollTop,
      document.body.scrollTop
    );
    let clientHeight = document.documentElement.clientHeight;

    if (scrollTop + clientHeight === scrollHeight) {
      if (this.state.next !== null) {
        this.getList(this.state.next);
      }
    }
  };

  renderBoardList = () => {
    const board = this.state.results.map(data => {
      return (
        <BoardList
          key={data.id}
          id={data.id}
          subject={data.subject}
          category={data.category}
          schoolName={data.school_name}
          postDate={data.post_date}
          content={data.content}
        />
      );
    });
    return board;
  };

  render() {
    return (
      <section className="board">
        <h2>
          Notice Board{" "}
          <span className="buttons" onClick={() => this.getSelectList()}>
            Data Update
          </span>
        </h2>

        {this.state.results ? this.renderBoardList() : "loading..."}
      </section>
    );
  }
}

export default Board;
