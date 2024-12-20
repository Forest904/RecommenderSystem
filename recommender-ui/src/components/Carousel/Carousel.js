import React from 'react';
import Slider from 'react-slick'; // React Slick carousel library
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import Card from '../Card/Card';

const Carousel = ({ recommendations = [] }) => {
    const settings = {
        dots: false,
        infinite: false,
        speed: 500,
        slidesToShow: 6,
        slidesToScroll: 1,
        responsive: [
            {
                breakpoint: 768,
                settings: { slidesToShow: 1 },
            },
            {
                breakpoint: 1024,
                settings: { slidesToShow: 2 },
            },
        ],
    };

    return (
        <Slider {...settings}>
            {recommendations.map(({ title, author, genres, plot, vote_average, vote_count, release_date, large_cover_url, type }, index) => (
            <Card
                key={index}
                title={title}
                image={large_cover_url}
                type={type}
            />
            ))}
        </Slider>
    );
};

export default Carousel;
