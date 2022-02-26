import asyncio
from asyncio import all_tasks, events, coroutines
from pyppeteer import launch
import check_install 
from lxml import html


async def main(url, target):
  
  
  browser = None
  code = check_install.read_config()
  if not code == 0:
     browser = await launch(headless=False, args=['--no-sandbox'], executablePath=str(code))
  else:
     browser = await launch(headless=False, args=['--no-sandbox'])
  page = await browser.newPage()
  await page.goto('https://steamdb.info/depot/731/history/?changeid=M:7992048448610181985')
  await page.waitFor(10000)
  text = await page.evaluate('''() => {return document.documentElement.innerText}''')
  with open("f.html", "w") as f:
      f.write(text)
      f.close()
  print(text)
  await browser.close()


def _cancel_all_tasks(loop: asyncio.AbstractEventLoop) -> None:
        to_cancel = all_tasks(loop)
        if not to_cancel:
              return

        for task in to_cancel:
              task.cancel()

        loop.run_until_complete(asyncio.gather(*to_cancel, loop=loop, return_exceptions=True))

        for task in to_cancel:
              if task.cancelled():
                   continue
              if task.exception() is not None:
                   loop.call_exception_handler({
                                'message': 'unhandled exception during asyncio.run() shutdown',
                                'exception': task.exception(),
                                'task': task,
                   })


def syncio():
        if events._get_running_loop() is not None:
                raise RuntimeError(
                        "asyncio.run() cannot be called from a running event loop")

        #if not coroutines.iscoroutine(main(depotid="731")):
        #        raise ValueError("a coroutine was expected, got {!r}".format(main(depotid="731")))

        loop = events.new_event_loop()
        try:
               events.set_event_loop(loop)
               return loop.run_until_complete(main(depotid="731"))
        finally:
               try:
                   _cancel_all_tasks(loop)
                   loop.run_until_complete(loop.shutdown_asyncgens())
               finally:
                   events.set_event_loop(None)
                   loop.close()
   

syncio()
