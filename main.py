"""Main entry point for LockIn AI focus detection system.

This module wires together all components of the system and provides
the main execution loop.
"""

import argparse
import sys
from typing import Optional

from focusai.config import load_config, Config
from focusai.logging_setup import setup_logging, get_logger
from focusai.capture.camera import create_capture
from focusai.preprocess.processor import create_preprocessor
from focusai.preprocess.features import create_feature_extractor
from focusai.inference.detector import create_detector
from focusai.ui.monitor import create_ui

logger = get_logger("main")


class LockInAISystem:
    """Main system coordinator for focus detection pipeline.
    
    Manages the complete pipeline from camera capture through inference
    to UI display.
    """
    
    def __init__(self, config: Config):
        """Initialize the LockIn AI system.
        
        Args:
            config: System configuration
        """
        self.config = config
        self.capture = None
        self.preprocessor = None
        self.feature_extractor = None
        self.detector = None
        self.ui = None
        logger.info("Initializing LockIn AI system")
    
    def initialize_components(self) -> None:
        """Initialize all system components."""
        logger.info("Initializing system components")
        
        # Create components
        self.capture = create_capture(self.config.capture)
        self.preprocessor = create_preprocessor(self.config.preprocess)
        self.feature_extractor = create_feature_extractor(self.config.preprocess)
        self.detector = create_detector(self.config.inference)
        self.ui = create_ui(self.config.ui)
        
        logger.info("All components initialized")
    
    def process_frame(self, frame) -> None:
        """Process a single frame through the pipeline.
        
        Args:
            frame: Raw frame from camera
        """
        # Preprocess frame
        processed_frame = self.preprocessor.preprocess(frame)
        
        # Extract features
        processed_frame = self.feature_extractor.extract(processed_frame)
        
        # Run inference
        focus_result = self.detector.detect(processed_frame)
        
        # Update UI
        self.ui.update(focus_result)
    
    def run(self) -> None:
        """Run the main focus detection loop.
        
        Continuously captures frames, processes them, and updates the UI
        until interrupted.
        """
        logger.info("Starting LockIn AI main loop")
        
        try:
            # Start components
            self.capture.start()
            self.ui.start()
            
            # Main processing loop
            for frame in self.capture.stream_frames():
                self.process_frame(frame)
                
                # Check if UI is still running
                if not self.ui.is_running:
                    logger.info("UI closed, stopping system")
                    break
        
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down")
        
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            raise
        
        finally:
            self.shutdown()
    
    def shutdown(self) -> None:
        """Cleanly shutdown all system components."""
        logger.info("Shutting down LockIn AI system")
        
        if self.capture:
            self.capture.stop()
        
        if self.ui:
            self.ui.stop()
        
        logger.info("Shutdown complete")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="LockIn AI - Real-time focus detection system"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Path to log file (logs to stdout if not specified)"
    )
    
    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="Camera device ID (default: 0)"
    )
    
    return parser.parse_args()


def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    setup_logging(level=args.log_level, log_file=args.log_file)
    logger.info("LockIn AI starting up")
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Override config with command line arguments
        if args.camera is not None:
            config.capture.camera_id = args.camera
        
        # Create and initialize system
        system = LockInAISystem(config)
        system.initialize_components()
        
        # Run main loop
        system.run()
        
        logger.info("LockIn AI shutdown successfully")
        return 0
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

