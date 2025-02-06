import React from 'react';
import Slider from 'react-slick';
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import Card from '../Card/Card';

// Material UI Imports
import { IconButton } from '@mui/material';
import ArrowBackIosNewIcon from '@mui/icons-material/ArrowBackIosNew';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';

// Custom Previous Arrow Component
const PrevArrow = ({ onClick }) => (
  <IconButton
    onClick={onClick}
    style={{
      position: 'absolute',
      top: '50%', // Center vertically
      transform: 'translateY(-50%)', // Adjust for button height
      left: '-40px', // Distance from left
      zIndex: 2, // Ensure it stays above slides
      backgroundColor: 'rgba(0,0,0,0.5)',
      color: 'white',
    }}
  >
    <ArrowBackIosNewIcon />
  </IconButton>
);

// Custom Next Arrow Component
const NextArrow = ({ onClick }) => (
  <IconButton
    onClick={onClick}
    style={{
      position: 'absolute',
      top: '50%', // Center vertically
      transform: 'translateY(-50%)', // Adjust for button height
      right: '-40px', // Distance from right
      zIndex: 2, // Ensure it stays above slides
      backgroundColor: 'rgba(0,0,0,0.5)',
      color: 'white',
    }}
  >
    <ArrowForwardIosIcon />
  </IconButton>
);

const Carousel = ({ recommendations = [] }) => {
  const settings = {
    dots: true,
    infinite: true,
    speed: 500,
    arrows: true, // Ensure arrows are enabled
    nextArrow: <NextArrow />,
    prevArrow: <PrevArrow />,
    slidesToShow: 6,
    slidesToScroll: 3,
    responsive: [
      {
        breakpoint: 1024,
        settings: { slidesToShow: 2 },
      },
      {
        breakpoint: 768,
        settings: { slidesToShow: 1 },
      },
    ],
  };

  return (
    <div style={{ position: 'relative' }}>
      <style>
        {`
          .slick-prev, .slick-next {
            display: none !important;
          }
        `}
      </style>
      <Slider {...settings}>
        {recommendations.map(
          ({ title, large_cover_url, type }, index) => (
            <Card key={index} title={title} image={large_cover_url} contentType={type} />
          )
        )}
      </Slider>
    </div>
  );
};

export default Carousel;
