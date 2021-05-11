/* eslint-disable jsx-a11y/alt-text */
import axios from "axios";
import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { Link } from 'react-router-dom';
import { BACKEND_SERVER_DOMAIN } from "../../../settings";

export default function SuggestFriends() {
    const user = useSelector((state) => state.user);
    const token = user.token;
    const [suggestions, setSuggestions] = useState();
    const [isLoading, setIsLoading] = useState(true)

    const getSuggestions = () => {
        let config = {
            headers: {
                "Content-Type": "application/json",
                Authorization: token,
            },
        };
        axios
            .get(BACKEND_SERVER_DOMAIN + "/api/friends/suggestions/", config)
            .then(function (response) {
                setSuggestions(response.data["friend_suggestions"].slice(0,3));
                setIsLoading(false)
            })
            .catch(function (err) {
                console.log(err);
                setIsLoading(false)
            });
    };

    useEffect(() => {
        getSuggestions();
    }, []);

    return !isLoading ? suggestions ? (
        <div>
            <h6 className="mt-3">Friend Suggestions</h6>
            <div className="card friend-suggestions">
                {suggestions.map((user, index) => (
                    <SuggestedFriendItem key={index} token={token} user={user}/>
                ))}
                <Link to={"/findfriends"} className="card-btn">Find more Friends</Link>
            </div>
        </div>
    ) : ("") : (
        <div className="slim-loading-bar"></div>
    );
}

export function SuggestedFriendItem({token, user}) {
    const [isReqSent, setIsReqSent] = React.useState(false)
    let btnRef = React.useRef()

    const sendFriendRequest = (id) => {
        btnRef.current.setAttribute("disabled", "disabled");
        let config = {
            headers: {
                "Content-Type": "application/json",
                Authorization: token,
            },
        };
        axios
            .post(
                BACKEND_SERVER_DOMAIN + "/api/friends/request/send/",
                JSON.stringify({ to_user: id }),
                config
            )
            .then(function (response) {
                setIsReqSent(true)
            })
            .catch(function (error) {
                console.log(error);
                btnRef.current.removeAttribute("disabled", "disabled");
            });
    };

    return (
        <div className="d-flex user">
            <img
                className="rounded-circle"
                src={BACKEND_SERVER_DOMAIN + user.avatar}
                alt={user.first_name +"'s avatar"}
            />
            <div>
                <h6>
                    <Link to={"/u/"+user.slug}>
                        {user.first_name} {user.last_name}
                    </Link>
                </h6>
                <span>{user.tagline}</span>
                <button
                    onClick={() => sendFriendRequest(user.id)}
                    className="btn btn-sm btn-outline-primary"
                    ref={btnRef}
                >
                    {isReqSent
                        ? "Request Sent"
                        : "Add as Friend"}
                </button>
            </div>
        </div>
    )
}