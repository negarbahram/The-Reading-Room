import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

/** Prevents a single page's rendering bug from blanking the entire app.
 * Without this, an uncaught error anywhere in the tree unmounts everything
 * (header, footer, nav — all of it), which is indistinguishable from the
 * app being broken. This confines that failure to the page content. */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Unhandled error in page content:', error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <div role="alert" className="text-center py-16 border border-red-300 bg-red-50 rounded-lg text-red-800 max-w-xl mx-auto">
          <p className="font-serif text-lg mb-2">Something went wrong loading this page.</p>
          <p className="text-sm">Please try navigating elsewhere and back, or refresh the page.</p>
        </div>
      );
    }
    return this.props.children;
  }
}
