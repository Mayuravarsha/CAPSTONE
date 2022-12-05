import React from "react";
import { useNavigate } from "react-router-dom";
//import DropFileInput from './components/drop-file-input/DropFileInput';
import "../../node_modules/bootstrap/dist/css/bootstrap.min.css";
import { useCallback,useState } from "react";
import Particles from "react-tsparticles";
import { loadFull } from "tsparticles";
import LoadingButton from "./components/drop-file-input/LoadingButton";
import axios from "axios";
import { useGlobalState,setGlobalState } from "../states";

const Home = ()=> {
    const [file, setfile] = useState()
    const [isLoading,setisLoading]=useState(false)
    const [violence,setViolence]=useState(0)
    const particlesInit = useCallback(async engine => {
        console.log(engine);
        await loadFull(engine);
    }, []);

    const particlesLoaded = useCallback(async container => {
        await console.log(container);
    }, []);
    const onFileChange = (files) => {
        setfile(files)
    }

    const navigate= useNavigate();
    
    async function sayHello(e) {
        //console.log(files);
        e.preventDefault()
        const formData = new FormData()
        formData.append('file', file)
        console.log(formData)
        setisLoading(true)
        await axios.post('http://localhost:5000/home',formData)
    .then(({data})=>
       setGlobalState("violence",data.data)
    )
        setisLoading(false)
        navigate("/result")
    };

    const buttonStyle = {
        border:"solid",
        background:"#2E4053",
        padding: "10px 10px",
        color:"white",
        height:"60px",
        cursor: "pointer",
        width: "100%",
        display: "flex",
        flexDirection:"column",
        alignItems: "center",
        justifyContent: "center",
       
      };
    return(
        <div className="Home">
                <Particles
                id="tsparticles"
                init={particlesInit}
                loaded={particlesLoaded}
                options={{
                    "fullScreen": {
                        "enable": true,
                        "zIndex": -1
                    },
                    background: {
                        color: {
                            value: "#6A5ACD",
                        },
                    },
                    fpsLimit: 120,
                    interactivity: {
                        events: {
                            onClick: {
                                enable: true,
                                mode: "push",
                            },
                            onHover: {
                                enable: false,
                                mode: "repulse",
                            },
                            resize: true,
                        },
                        modes: {
                            push: {
                                quantity: 4,
                            },
                            repulse: {
                                distance: 200,
                                duration: 0.4,
                            },
                        },
                    },
                    particles: {
                        color: {
                            value: "#ffffff",
                        },
                        links: {
                            color: "#ffffff",
                            distance: 150,
                            enable: true,
                            opacity: 0.5,
                            width: 1,
                        },
                        collisions: {
                            enable: true,
                        },
                        move: {
                            directions: "none",
                            enable: true,
                            outModes: {
                                default: "bounce",
                            },
                            random: false,
                            speed: 3,
                            straight: false,
                        },
                        number: {
                            density: {
                                enable: true,
                                area: 800,
                            },
                            value: 80,
                        },
                        opacity: {
                            value: 0.5,
                        },
                        shape: {
                            type: "circle",
                        },
                        size: {
                            value: { min: 1, max: 5 },
                        },
                    },
                    detectRetina: true,
                }}
            />
            <h1 className ="header">Violence Detection</h1>
            <div className="box">
                <h2 className="header" >
                    Input Your File Here!!!
                </h2>
                <input type='file' onChange={(e) => setfile(e.target.files[0])} />
                
                
            </div>

           {
            isLoading?<LoadingButton/>:<button  className="rounded-corners" style={buttonStyle}  border-radius= {"15px 15px"} onClick={sayHello}> Detect Violence</button>
           }

        </div>
    )
};

export default Home;