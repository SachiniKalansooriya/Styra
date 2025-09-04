export const weatherThemes = {
  sunny: {
    primary: '#FF9800',
    secondary: '#FFC107',
    background: ['#FFE082', '#FFF3E0'],
    surface: '#FFFFFF',
    text: '#333333',
    accent: '#FF5722',
    shadow: 'rgba(255, 152, 0, 0.3)',
  },
  rainy: {
    primary: '#607D8B',
    secondary: '#78909C',
    background: ['#B0BEC5', '#CFD8DC'],
    surface: '#FFFFFF',
    text: '#37474F',
    accent: '#00ACC1',
    shadow: 'rgba(96, 125, 139, 0.3)',
  },
  cloudy: {
    primary: '#9E9E9E',
    secondary: '#BDBDBD',
    background: ['#F5F5F5', '#FAFAFA'],
    surface: '#FFFFFF',
    text: '#424242',
    accent: '#5C6BC0',
    shadow: 'rgba(158, 158, 158, 0.3)',
  },
  party: {
    primary: '#E91E63',
    secondary: '#F06292',
    background: ['#FCE4EC', '#F8BBD9'],
    surface: '#FFFFFF',
    text: '#880E4F',
    accent: '#FF4081',
    shadow: 'rgba(233, 30, 99, 0.4)',
  },
};

export const getThemeForWeather = (weatherCondition) => {
  const condition = weatherCondition?.toLowerCase();
  
  if (condition?.includes('rain') || condition?.includes('storm')) {
    return weatherThemes.rainy;
  }
  if (condition?.includes('cloud') || condition?.includes('overcast')) {
    return weatherThemes.cloudy;
  }
  if (condition?.includes('clear') || condition?.includes('sun')) {
    return weatherThemes.sunny;
  }
  
  return weatherThemes.sunny; // default
};