// web-app/src/App.test.tsx
import { render } from '@testing-library/react';
import App from './App';

// Basic Vitest/Jest syntax
it('renders correctly and matches snapshot', () => {
  const { asFragment } = render(<App />);
  expect(asFragment()).toMatchSnapshot();
});
