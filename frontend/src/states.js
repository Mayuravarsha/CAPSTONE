import { createGlobalState } from "react-hooks-global-state";

const { setGlobalState, useGlobalState } =createGlobalState({
    "violence":0
})

export { setGlobalState,useGlobalState };
