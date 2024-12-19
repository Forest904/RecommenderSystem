import React from 'react';
import Slider from 'react-slick'; // React Slick carousel library
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import Card from '../Card/Card';

const Carousel = ({ recommendations = [] }) => {
    const settings = {
        dots: true,
        infinite: true,
        speed: 500,
        slidesToShow: 6,
        slidesToScroll: 2,
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
            {recommendations.map((item, index) => (
                <Card key={index} {...item} />
            ))}
        </Slider>
    );
};

export default Carousel;
