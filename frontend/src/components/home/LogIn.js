import axios from "axios";
import React, { useRef, useState } from "react";
import { Helmet } from "react-helmet";
import { useDispatch } from "react-redux";
import { Link, useHistory } from "react-router-dom";
import logo from "../../assets/images/logo.png";
import { setUser } from "../../redux/actions";
import { BACKEND_SERVER_DOMAIN } from "../../settings";
import InputField from "../../utils/InputField";
import { themeApply } from '../global/ThemeApply';
import FinishSignUp from './FinishSignUp';

function LogIn() {
    const dispatch = useDispatch();
    const history = useHistory();

    themeApply();
    
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [apiResponse, setAPIResponse] = useState();
    const [isSecondStageSignUpPending,setIsSecondStageSignUpPending] = useState(false)

    const handleEmail = ({ target }) => {
        setEmail(target.value);
    };
    const handlePassword = ({ target }) => {
        setPassword(target.value);
    };
    let btnRef = useRef();

    const handleLogIn = () => {

        if (!email || !password) {
            setAPIResponse(
                <div className="fw-bold text-danger text-sm pb-2">
                    Ooops! Make sure you have typed in your email and password.
                </div>);
            return;
        }

        if (btnRef.current) {
            btnRef.current.setAttribute("disabled", "disabled");
        }
        let config = {
            headers: {
                "Content-Type": "application/json",
            },
        };
        axios
            .post(
                BACKEND_SERVER_DOMAIN + "/api/user/login/",
                JSON.stringify({ email: email, password: password }),
                config
            )
            .then(function (response) {
                dispatch(setUser(response.data));
                if (response.data.avatar != null) {
                    history.push("/dashboard");
                } else {
                    setIsSecondStageSignUpPending(true)
                }
            })
            .catch(function (error) {
                setAPIResponse(
                    <div className="fw-bold text-danger text-sm pb-2">
                        Unable to login, make sure your email and password are correct.
                    </div>
                );
                if (btnRef.current) {
                    btnRef.current.removeAttribute("disabled");
                }
            });
    };

    return (
        <section className="login bg-social-icons">
            <Helmet>
                <title>Log In to socialnetwork!</title>
            </Helmet>
            <div className="container">
                <div className="col-lg-5 col-md-12 col-sm-12">
                    <img src={logo} className="logo" />
                    {
                        (isSecondStageSignUpPending) ? <FinishSignUp /> 
                        :
                        <div className="card">
                            <h3>Log in</h3>
                            {apiResponse}
                            <InputField
                                label="Email"
                                onChange={handleEmail}
                                name="email"
                                type="email"
                                placeholder="you@company.com"
                            />
                            <InputField
                                label="Password"
                                onChange={handlePassword}
                                name="password"
                                type="password"
                            />
                            <button
                                type="submit"
                                ref={btnRef}
                                onClick={handleLogIn}
                                className="btn btn-primary btn-main"
                            >
                                Log in!
                            </button>
                            <span>
                                or would you like to <Link to="#">Reset Password</Link>{" "}
                                or <Link to="/">Sign Up</Link>
                            </span>
                        </div>
                    }
                </div>
            </div>
        </section>
    );
}

export default LogIn;
