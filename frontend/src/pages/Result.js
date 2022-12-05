import React from "react";
import { useCallback } from "react";
import Particles from "react-tsparticles";
import { loadFull } from "tsparticles";
import { useGlobalState } from "../states";
import { PieChart } from 'react-minimal-pie-chart';

const Result = () =>{
    const particlesInit = useCallback(async engine => {
        console.log(engine);
        await loadFull(engine);
    }, []);

    const particlesLoaded = useCallback(async container => {
        await console.log(container);
    }, []);
    const [violence]=useGlobalState("violence")
    const violenceText=(violence > 0.5)?"Violent":"Non Violent"
    let data=[
        { title: 'Violent', value: violence*100, color: '#E38627' },
        { title: 'Non - Violent', value: (1 - violence)*100, color: '#C13C37' },
    ]
    data=data.filter((object)=>object.value > 0)
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
                <h1 className ="header">Result</h1>
                <div className="box">
                    {
                        <h2 className="header" >
                            The Video is {violenceText} 
                        </h2>
                    
                    }            
                </div>
                <PieChart
                center={[50, 50]}
                //label={(label)=>"violence"}
                label={(data) => data.dataEntry.title}
                startAngle={0}
                viewBoxSize={[100, 100]}
                labelStyle={{
                    fontSize: "2px",
                    fontColor: "FFFFFA",
                    fontWeight: "800",
                  }}
                data={data}
                />
            </div>
        
    )

}
export default Result;