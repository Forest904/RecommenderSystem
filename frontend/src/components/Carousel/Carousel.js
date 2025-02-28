import React, { useContext } from 'react';
import Slider from 'react-slick';
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import Card from '../Card/Card';

// Material UI Imports
import { IconButton } from '@mui/material';
import ArrowBackIosNewIcon from '@mui/icons-material/ArrowBackIosNew';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';
import { ThemeContext } from '../../ThemeContext';

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
  const { darkMode } = useContext(ThemeContext);

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
          .slick-dots li button:before {
            color: ${darkMode ? 'white' : 'black'} !important;
            opacity: 0.75;
          }
          .slick-dots li.slick-active button:before {
            color: ${darkMode ? 'white' : 'black'} !important;
            opacity: 1;
          }
        `}
      </style>
      <Slider {...settings}>
        {recommendations.map(
          ({ title, large_cover_url, type, link }, index) => (
            <Card key={index} title={title} image={large_cover_url} contentType={type} link={link} />
          )
        )}
      </Slider>
    </div>
  );
};

export default Carousel;
