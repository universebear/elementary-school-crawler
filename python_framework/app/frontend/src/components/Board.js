import React, { Component } from "react";
import { connect } from "react-redux";
import { getBoardList } from "../store/modules/board";
class Board extends Component {
  componentDidMount() {
    this.updateBoard();
  }
  updateBoard = () => {
    const { getBoardList } = this.props;
    getBoardList();
  };
  render() {
    return (
      <section>
        <p>test page</p>
        {/* <button onClick={this.updateBoard()} type="button"> */}
        {console.log(this.props)}
        {/* </button> */}
      </section>
    );
  }
}

const mapStateToProps = state => ({
  boardList: state.board.boardList,
  next: state.board.next,
  previous: state.board.previous,
  count: state.board.count
});

const mapDispatchToProps = dispatch => ({
  getBoardList: () => dispatch(getBoardList())
});

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Board);
