import axios from "axios";
import { getMetadata } from 'page-metadata-parser';
import React, { useEffect, useRef, useState } from "react";
import { LazyLoadImage } from 'react-lazy-load-image-component';
import { Link } from 'react-router-dom';
import { BACKEND_SERVER_DOMAIN } from "../../../settings";
import { timeSince } from "../../../utils/timesince";
import CommentComponent from "./Comment";

const TimelinePost = ({ user, post, expanded}) => {
    const [isLiked, setIsLiked] = useState(false);
    const [likesCount, setLikesCount] = useState(0);
    const [comments, setComments] = useState();
    const [showComments, setShowComments] = useState(false);
    const [isLoadingComments,setIsLoadingComments] = useState(false);
    const [embedUrls,setEmbedUrls] = useState();
    const [isDeleted, setIsDeleted] = useState(false);
    let btnRef = useRef();

    useEffect(() => {
        if(!isDeleted) {
            if(post.likes) {
                setIsLiked(post.likes.user_ids && post.likes.user_ids.includes(user.id));
                setLikesCount((post.likes.user_ids && post.likes.user_ids != null) ? post.likes.user_ids.length : 0);
            }
            let urlRegEx = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
            const urls = [...post.post_text.matchAll(urlRegEx)]
            let links = []
            if (urls) {
                urls.map(async (url, index) => {
                    const domino = require('domino');
                    const response = await fetch(url[0], {
                        mode: 'no-cors' // 'cors' by default
                    });
                    const html = await response.text();
                    const doc = domino.createWindow(html).document;
                    const metadata = getMetadata(doc, url);
                    links.push({"title":metadata.title,
                        "description":metadata.description,
                        "url":url[0]})
                    if (urls.length == index+1) setEmbedUrls(links);
                })
            }
            if (expanded) {
                commentsToggle()
            }
        }
    }, []);

    const likePost = () => {
        if (btnRef.current) {
            btnRef.current.setAttribute("disabled", "disabled");
        }
        let config = {
            headers: {
                "Content-Type": "application/json",
                Authorization: user.token,
            },
        };
        axios
            .put(BACKEND_SERVER_DOMAIN + "/api/post/" + post.id + "/", {}, config)
            .then(function (response) {
                let like = isLiked ? false : true;
                setIsLiked(like);
                if (like) {
                    setLikesCount(likesCount+1);
                } else {
                    setLikesCount(likesCount-1);
                }
                if (btnRef.current) {
                    btnRef.current.removeAttribute("disabled");
                }
            })
            .catch(function (err) {
                console.log(err);
            });
    };

    const commentsToggle = () => {
        if (comments) {
            setShowComments(!showComments);
        } else {
            if (!isLoadingComments) {setIsLoadingComments(true)}
            axios.get(BACKEND_SERVER_DOMAIN + "/api/" + post.id + "/comments/", {headers:{Authorization: user.token}})
                .then(function (response) {
                    setComments(response.data.comments)
                    if (response.data.comments.length == 0) {
                        setIsLoadingComments(false);
                    } else {
                        setShowComments(true)
                    }
                })
                .catch((err) => {
                    console.log(err.response)
                    setIsLoadingComments(false);
                })
        }
    }

    const commentField = useRef();
    const postComment = (parent) => {
        let commentText = commentField.current.value;
        if (commentText) {
            let formData = new FormData();
            formData.append("comment_text", commentText);
            formData.append("comment_parent", parent);
            let config = { headers: {
                'Content-Type': 'multipart/form-data',
                Authorization: user.token,   
            }}
            axios.post(BACKEND_SERVER_DOMAIN+'/api/'+post.id+'/comments/new/',formData, config)
                .then(function (response) {
                    // Post has been made successfully
                    if (comments) 
                    {
                        // If we already have comments
                        comments.push(response.data);
                        // React only rerenders if pointer to field is changed so 
                        // we have to make a new array
                        let newArr = [...comments];
                        setComments(newArr);
                    }
                    else {
                        setComments(Array.of(response.data));
                    }
                    commentField.current.value = "";
                    setShowComments(true)
                })
                .catch(function (error) {
                    console.log(error);
                });
        } else {
            console.log("empty field");
        }
    }

    const deletePost = () => {
        let config = {
            headers: {
                "Content-Type": "application/json",
                Authorization: user.token,
            },
        };
        axios
            .delete(
                BACKEND_SERVER_DOMAIN +
                    "/api/post/" +
                    post.id + "/",
                config
            )
            .then(function (response) {
                if (response.data.action) {
                    setIsDeleted(true);
                }
            })
            .catch(function (err) {
                console.log(err);
            });
    }

    function splicedArray(array,index) {
        let nArr = [...array];
        nArr.splice(0,index+1);
        return nArr;
    }

    return (!isDeleted) ? (
        <article className="post card">
            <div className="d-flex userbar">
                <LazyLoadImage
                    loading="lazy"
                    className="rounded-circle"
                    src={BACKEND_SERVER_DOMAIN + post.user.avatar}
                    alt={post.user.first_name + "'s avatar"}
                />
                <div>
                    <h6>
                        <Link to={"/u/"+post.user.slug}>{post.user.first_name} {post.user.last_name}</Link>
                    </h6>
                    <span>{timeSince(post.created)}</span>
                </div>
                <div className="more-options">
                    <div className="dropleft">
                        <button
                            className="post-actions"
                            type="button"
                            id={"options"+post.id}
                            data-toggle="dropdown"
                            aria-haspopup="true"
                            aria-expanded="false"
                        >
                            <i className="fas fa-ellipsis-h"></i>
                        </button>
                        <div
                            className="dropdown-menu"
                            aria-labelledby={"options"+post.id}
                        >
                            <Link className="dropdown-item" to={"/post/"+post.id}>
                                View Post
                            </Link>
                            {(user.id == post.user_id) ? <button className="dropdown-item"
                            onClick={deletePost}>
                                Delete
                            </button> : ""}
                        </div>
                    </div>
                </div>
            </div>
            <div>
                <p className="post-content">{post.post_text}</p>
                {(embedUrls) ? (embedUrls.map((url, index) => (
                    <a className="url" href={url.url} key={index} target="_blank">
                        <div>
                            <div className="utitle"><i className="fas fa-external-link-alt"></i> {url.title}</div>
                            {(url.description) ? <div className="udescription">{url.description}</div> : ""}
                            <div className="uurl">{url.url}</div>
                        </div>
                    </a>
                ))) : ""}
            </div>
            {post.post_image ? (
                <LazyLoadImage src={BACKEND_SERVER_DOMAIN +post.post_image} className="rounded post-picture" alt={post.user.first_name + "'s post picture"} />
            ) : (
                ""
            )}
            <div className="d-flex post-actions">
                <button
                    onClick={commentsToggle}>
                    <i className="far fa-comment-alt"></i>{(comments) ? (comments.length == 0) ? "No " : comments.length +" " : ""}Comments
                </button>
                <button
                    ref={btnRef}
                    onClick={likePost}
                    className={
                        isLiked
                            ? "btn btn-light btn-light-accent"
                            : "btn btn-light"
                    }
                >
                    <i className="far fa-thumbs-up"></i>
                    {likesCount > 0 ? likesCount+' ' : ''}Like
                    {likesCount > 1 ? "s" : ""}
                </button>
                <button>
                    <i className="far fa-share-square"></i>Share
                </button>
            </div>
            { (post.likes) ? 
                <div className="likedBy">Liked by&nbsp;
                        {post.likes.users.slice(0,2).map((user, index)=> (
                            <span key={user.id}>
                                <Link to={"/u/"+user.slug} key={user.id}>
                                    {user.first_name} {user.last_name}
                                </Link>
                                {(post.likes.users.length > 1 && index==0) ?", ":""}
                            </span>
                        ))} {(post.likes.users.length > 2) ? " and "+(likesCount-2)+" others": ""}
                </div> : ""
            }
            <div className={(isLoadingComments) ? "slim-loading-bar":""}></div>
            
            {
                showComments && typeof comments == "object" ?
                    <div className="each-comment parent-comment">
                        {comments.slice().map((comment, index) => (
                            <div key={comment.id}>{(comment.comment_parent == 0) ?
                                    <CommentComponent 
                                        key={comment.id}
                                        comment={comment}
                                        user={user}
                                        allComments={splicedArray(comments,index)}/>
                            : ''}
                            {(Number(index+1) == Number(comments.length) && isLoadingComments) ? setIsLoadingComments(false) : ''}
                            </div>                       
                        ))}
                    </div>
                : <div></div>
            }
            <div className="post-comment">
                <div className="d-flex">
                    <input type="text" ref={commentField} placeholder="Write your comment..." />
                    <button onClick={() => postComment(0)}>
                        <i className="far fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        </article>
    ) : <article className="post card text-center text-muted">Post is removed.</article>;
};

export default TimelinePost;
