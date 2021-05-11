import axios from 'axios';
import React from 'react';
import { Helmet } from "react-helmet";
import { useSelector } from 'react-redux';
import { useParams } from 'react-router-dom';
import { BACKEND_SERVER_DOMAIN } from '../../../settings';
import LeftSidebar from "../LeftSidebar";
import Navbar from "../Navbar";
import TimelinePost from './TimelinePost';

export default function PostPage() {
    const {post_id} = useParams();
    const user = useSelector((state) => state.user);
    const [post,setPost] = React.useState();

    React.useEffect(() => {
        window.scrollTo(0, 0);
        let config = { headers: {
            'Content-Type': 'application/json',
            Authorization: user.token,   
        }};
        axios.get(BACKEND_SERVER_DOMAIN + '/api/post/'+post_id+"/", config)
            .then(function (response) {
                setPost(response.data);
            })
            .catch(function (err) {
                console.log(err);
            });
    },[])

    return (
        <section className="profile-page">
            <Helmet>
                <title>{(post) ? post.user.first_name + " " +post.user.last_name : "User"}'s Post</title>
            </Helmet>
            <Navbar />
            <div className="navbar-spacer"></div>
            <div className="container">
                <div className="row">
                    <div className="col-lg-3 col-12">
                        <LeftSidebar active="0"/>
                    </div>
                    <div className="col-lg-6 col-12 timeline">
                        {(post) ? <TimelinePost user={user} post={post} expanded={true}/>:""}
                    </div>
                </div>
            </div>
        </section>
    )
}
