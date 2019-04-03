import axios from "axios";
import { handleActions } from "redux-actions";
const GET_BOARDLIST = "GET_BOARDLIST";
const GET_BOARD_FAILURE = "GET_BOARD_FAILURE";

function getBoardAPI() {
  return axios.get(`/api/board/`);
}

export const getBoardList = () => dispatch => {
  dispatch({ type: GET_BOARDLIST });
  return getBoardAPI()
    .then(response => {
      dispatch({
        type: GET_BOARDLIST,
        boardList: response.data.results,
        next: response.data.next,
        previous: response.data.previous,
        count: response.data.count
      });
    })
    .catch(error => {
      dispatch({
        type: GET_BOARD_FAILURE,
        payload: error
      });
    });
};

const initialState = {
  boardList: [],
  next: null,
  previous: null,
  count: 0
};

export default handleActions(
  {
    [GET_BOARDLIST]: (state, action) => {
      return {
        ...state,
        boardList: action.boardList,
        next: action.next,
        previous: action.previous,
        count: action.count
      };
    }
  },
  initialState
);
